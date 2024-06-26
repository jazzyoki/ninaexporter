import requests
import json
from base64 import b64decode
from prometheus_client import start_http_server, Gauge
import time
import yaml, random


NINASERVER = "127.0.0.1"
EXPORTPORT = 8000
FREQUENCY = 60
FREQGUIDER = 10
FREQIDLE = 120
DEBUG = 0
IMAGEPATH = ''

guider_rms_total_pixel = Gauge('nina_guider_rms_total_pixel', "Total RMS error guiding in pixel")
guider_rms_total_arc = Gauge('nina_guider_rms_total_arc', "Total RMS error guiding in arcsec")
guider_rms_dec_arc = Gauge('nina_guider_dec_arc', "Declination error in arcsec")
guider_rms_ra_arc = Gauge('nina_guider_ra_arc', "Rectascension error in arcsec")
image_hfr = Gauge( 'nina_image_hfr', "Image HFR", ['target_name','filter_name'])
image_stars = Gauge( 'nina_image_stars', "Number of stars detected in current image", ['target_name','filter_name'])
image_mean = Gauge( 'nina_image_mean', "Mean value of the current image", ['target_name','filter_name'])
nina_up_gauge = Gauge( 'nina_up', "Nina is online [0,1]")
weather_skytemperature = Gauge( 'nina_weather_skytemperature', "Sky Temperature")
weather_temperature = Gauge( 'nina_weather_temperature', "Temperature")
weather_humidity = Gauge( 'nina_weather_humidity', "Humidity")
weather_dewpoint = Gauge( 'nina_weather_dewpoint', "Dew Point")
safety_issafe = Gauge('nina_safety_issafe', "Safety Monitor Safe Reporting")
nina_dome_shutter = Gauge('nina_dome_shutter', "Dome Shutter status")
last_index:int = -1
nina_up:int =0

targetdict = {}

def checkOnline() -> int:
    url = "http://" + NINASERVER + ":1888/api/"
    try:
        x = requests.get(url, timeout=(5,10))
        if x.status_code!=200:
            if DEBUG: print("setting offline")
            return 0
        if nina_up==0:
            if DEBUG: print("setting online")
        return 1
    except:
        if DEBUG: print("setting offline")
        return 0
    return 0

def getJSON( property:str , myobj:dict ):
    url = "http://" + NINASERVER + ":1888/api/" + property
    try:
        x = requests.get(url, myobj, timeout=(5,10))
        if x.status_code!=200:
            return None
        return json.loads(x.content.decode())
    except:
        return None

def get_metrics_rms( nina:int ) -> None:
    pixel:float = 0.0
    arc:float = 0.0
    dec:float = 0.0
    ra:float = 0.0
    if not nina:
        guider_rms_total_pixel.set(0 )
        guider_rms_total_arc.set( 0 )
        guider_rms_ra_arc.set(0)
        guider_rms_dec_arc.set(0)
        return
    
    if DEBUG:
        arc = random.random()*1.8
        dec = random.random()*1.8
        ra = random.random()*1.8
        data = getJSON("equipment", {'property': 'guider'})
    else:
        data = getJSON("equipment", {'property': 'guider'})
        if data==None:
            return
        rmserror = data['Response']['RMSError']
        if rmserror!=None:
            # Total
            message = rmserror['Total']
            pixel =  float(message['Pixel'])
            arc = float(message['Arcseconds'])
            # Dec
            message = rmserror['Dec']
            dec = float(message['Arcseconds'])
            # RA
            message = rmserror['RA']
            ra = float(message['Arcseconds'])

    guider_rms_total_pixel.set(pixel )
    guider_rms_total_arc.set( arc )
    guider_rms_ra_arc.set(ra)
    guider_rms_dec_arc.set(dec)

def get_metrics_weather( nina:int ) -> None:
    if nina==0:
        weather_skytemperature.set( 0 )
        weather_temperature.set( 0 )
        weather_dewpoint.set( 0 )
        weather_humidity.set( 0 )
        return
    data = getJSON("equipment", {'property': 'weather'})
    if data==None:
        return
    try:
        message = data['Response']
        weather_skytemperature.set( float(message['SkyTemperature']))
        weather_temperature.set( float(message['Temperature']))
        weather_dewpoint.set( float(message['DewPoint'] ))
        weather_humidity.set( float(message['Humidity']))
    except:
        print("error fetching weather")
    
def get_metrics_dome( nina:int ) ->None:
    if not nina:
        nina_dome_shutter.set( -1 )
        return
    data = getJSON("equipment", {'property': 'dome'})
    if data==None:
        return
    try:
        message = data['Response']
        nina_dome_shutter.set( float(message['ShutterStatus']))
    except:
        print("error fetching dome")
    
def get_metrics_safety ( nina:int ) ->None:
    if not nina:
        safety_issafe.set(-1)
    try:
        data = getJSON("equipment", {'property': 'safetymonitor'})
        if data==None:
            return
        message = data['Response']
        safety = 0
        if message['IsSafe']:
            safety = 1
        #print( safety )
        safety_issafe.set( message['IsSafe'] )
    except:
        print("error fetching safety")


def get_metrics_imagestats( nina:int )->None:
    global last_index
    global targetdict
    stars = 0
    hfr = 0.0
    mean = 0
    target = ''
    fname = ''
    if not nina:
        return
 
    if DEBUG:
        stars = random.randint(80,200)
        hfr = random.random()* 1.5+2.0
        mean = random.randint( 600, 700 )
        target='M99'
        targetdict['M99'] = 1
    else:
        data = getJSON("history", {'property': 'count'})
        if data==None:
            return
        #print( data )
        idx = data['Response']['Count'] - 1
        if idx<0 or idx==last_index:
            return
    
        last_index = idx
        data = getJSON("history", {'property': 'list', 'parameter': idx})['Response'][0]
        if data==None:
            return
        target = data['TargetName']
        fname = data['Filter']
        targetdict[ target ] = 1
        stars = int(data['Stars'])
        hfr= float(data['HFR'])
        mean = int(data['Mean'])
    image_stars.labels(target_name=target,filter_name=fname).set( stars )
    image_hfr.labels(target_name=target,filter_name=fname).set( hfr )
    image_mean.labels(target_name=target,filter_name=fname).set( mean )
 

def get_image( nina:int ) -> None:
    global last_index
    if nina==0 or last_index<0:
        return
    try:
        data = getJSON("equipment", {'property': 'image', 'parameter': '70', 'index': last_index})
        if data==None:
            return
        if len(data['Response'])<100:
            return
        imageb64 = data['Response']
        bytes = b64decode(imageb64)
        f = open(IMAGEPATH, 'wb')
        f.write(bytes)
        f.close()
    except:
        return

def set_nina_offline() -> None:
    global targetdict
    global last_index
    for target in targetdict:
        #print( "setting {} to zero".format(target))
        image_stars.labels(target_name=target).set( 0 )
        image_hfr.labels(target_name=target).set( 0 )
        image_mean.labels(target_name=target).set( 0 )
    targetdict.clear()
    last_index = -2

if __name__ == '__main__':
    with open("config.yaml", "r" ) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        #print(config)
        NINASERVER = config['nina_server']
        EXPORTPORT = config['export_port']
        FREQUENCY = config['frequency']
        FREQGUIDER = config['frequency_guider']
        FREQIDLE = config['frequency_idle']
        DEBUG = config['debug']
        IMAGEPATH = config['imagepath']

    print( "exporting at port {0}".format(EXPORTPORT) )
    if DEBUG: print("debug mode ON")
    start_http_server(EXPORTPORT)
    time_left: int = 0
    while True:
        try:
            switchstate = nina_up
            nina_up = checkOnline()
            nina_up_gauge.set( int(nina_up) )
            #check if we are set to offline
            if switchstate!=nina_up and nina_up==0:
                set_nina_offline()

            long_metrics = False
            if time_left<=0:
                if DEBUG: print("get long metrics")
                time_left = FREQUENCY
                long_metrics = True

            get_metrics_rms( nina_up )
            get_metrics_safety( nina_up )
            get_metrics_dome( nina_up )
            if long_metrics: 
                get_metrics_imagestats( nina_up )
                get_image( nina_up )
                get_metrics_weather( nina_up )
                    
        except:
            if DEBUG: print('error getting metrics')
            
        if time_left<FREQGUIDER:
            #print("sleep itchy")
            time.sleep(time_left)
            time_left = 0
        else:
            if nina_up:
                if DEBUG: print(" sleep short")
                time.sleep(FREQGUIDER)
                time_left -= FREQGUIDER
            else:
                if DEBUG: print( "sleep long")
                time.sleep(FREQIDLE)
    
	

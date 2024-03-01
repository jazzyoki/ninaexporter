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

guider_rms_total_pixel = Gauge('nina_guider_rms_total_pixel', "Total RMS error guiding in pixel")
guider_rms_total_arc = Gauge('nina_guider_rms_total_arc', "Total RMS error guiding in arcsec")
guider_rms_dec_arc = Gauge('nina_guider_dec_arc', "Declination error in arcsec")
guider_rms_ra_arc = Gauge('nina_guider_ra_arc', "Rectascension error in arcsec")
image_hfr = Gauge( 'nina_image_hfr', "Image HFR", ['target_name','ninaup'])
image_stars = Gauge( 'nina_image_stars', "Number of stars detected in current image", ['target_name','ninaup'])
image_mean = Gauge( 'nina_image_mean', "Mean value of the current image", ['target_name','ninaup'])
nina_up_gauge = Gauge( 'nina_up', "Nina is online [0,1]")

last_index = -1
nina_up =0

def getJSON(property, myobj):
    global nina_up
    url = "http://" + NINASERVER + ":1888/api/" + property
    nina_up=1
    try:
        x = requests.get(url, myobj)
        if x.status_code!=200:
            return None
        return json.loads(x.content.decode())
    except:
        #print("setting offline")
        nina_up=0
        return None

def get_metrics_rms():
    global nina_up
    pixel = 0.0
    arc = 0.0
    dec = 0.0
    ra = 0.0
    if DEBUG:
        arc = random.random()*1.8
        nina_up = 1
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
    nina_up_gauge.set( int(nina_up) )


def get_metrics_imagestats():
    global last_index
    stars = 0
    hfr = 0.0
    mean = 0
    data = getJSON("history", {'property': 'count'})
    global nina_up
    target = ''
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
    stars = int(data['Stars'])
    hfr= float(data['HFR'])
    mean = int(data['Mean'])
    image_stars.labels(target_name=target,ninaup=nina_up).set( stars )
    image_hfr.labels(target_name=target,ninaup=nina_up).set( hfr )
    image_mean.labels(target_name=target,ninaup=nina_up).set( mean )

if __name__ == '__main__':
    with open("config.yaml", "r" ) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        #print(config)
        NINASERVER = config['nina_server']
        EXPORTPORT = config['export_port']
        FREQUENCY = config['frequency']
        FREQGUIDER = config['frequency_guider']
        FREQIDLE = config['frequency_idle']

    print( "exporting at port {0}".format(EXPORTPORT) )
    start_http_server(EXPORTPORT)
    time_left = FREQUENCY
    while True:
        get_metrics_rms()
    
        if time_left<=0 and nina_up:
            #print("get long metrics")
            get_metrics_imagestats()
            time_left = FREQUENCY
        
        if time_left<FREQGUIDER:
            #print("sleep itchy")
            time.sleep(time_left)
            time_left = 0
        else:
            if nina_up:
                #print(" sleep short")
                time.sleep(FREQGUIDER)
                time_left -= FREQGUIDER
            else:
                #print( "sleep long")
                time.sleep(FREQIDLE)
    
	
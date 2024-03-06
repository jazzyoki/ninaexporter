import requests
import json
import http.client
import urllib
import os
from base64 import b64decode

APPTOKEN = "xxxxx"
USERKEY  = "xxxxx"
NINAHOST = "127.0.0.1"
PREVIEW  = 'preview.jpg'
mytmpdir = os.environ['TEMP']
imagePath = mytmpdir + '\\' + PREVIEW

def getJSON(property, myobj):
	url = "http://" + NINAHOST + ":1888/api/" + property
	x = requests.get(url, myobj)
	return json.loads(x.content.decode())

def writePreview(image, path):
	bytes = b64decode(image)
	f = open(path, 'wb')
	f.write(bytes)
	f.close()

def sendPushover(msg, image):
	r = requests.post("https://api.pushover.net/1/messages.json", data = {
	"token": APPTOKEN,
	"user": USERKEY,
	"message": msg
	},
	files = {
	"attachment": ("Preview", open(imagePath, "rb"), "image/jpeg")
	})
	return r


#currentFrameNr = data['Response']['Count'] - 2
#data = getJSON("history", {'property': 'list', 'parameter': currentFrameNr})
#message =  "Id: "     + str(data['Response'][0]["Id"]) + "\n"
#message += "Stars: "  + str(data['Response'][0]["Stars"]) + "\n"
#message += "Median: " + str(data['Response'][0]["Median"]) + "\n"
#message += "File: "   + data['Response'][0]["Filename"]

#data = getJSON("equipment", {'property': 'guider'})['Response']

#message = str(data['RMSError'])
#data = getJSON("equipment", {'property': 'image', 'parameter': '10'})
#print(data['Error'])
#imageb64 = data['Response']
#writePreview(imageb64, imagePath)
#print( message )
#ret = sendPushover(message, imagePath)
#print(str(ret.status_code) + " " + ret.reason)

#if os.path.exists(imagePath):
#	os.remove(imagePath)
if __name__ == '__main__':
	print( "lets go" )
	data = getJSON("equipment", {'property': 'safetymonitor'})['Response']
	message = data
	print(message)
	#data = getJSON("history", {'property': 'count'})['Response']
	#print ( data)
	#data = getJSON("history", {'property': 'list', 'parameter': 12})['Response']
	#if len(data)>0:
	#	print (data[0])
	#else:
	#	print( "nodata")
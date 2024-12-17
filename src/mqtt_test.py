#pip install paho-mqtt  --break-system-packages
#import context  # Ensures paho is in PYTHONPATH

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json

mqttIP = "192.168.10.51"
maintopic = 'rover/'
cmdtopic ='cmd'
statustopic = 'status'


receiver = None
test = 199
mapselected = None

def getMqttCmd():
	global receiver
	return receiver;
	
def getMqttTest():
	global test
	return test;
	
def getMapSelected():
	return mapselected
	
def mqttsend(utopic,payload,flagretain=False): 
	try:
		publish.single(maintopic+utopic, payload, hostname = mqttIP,retain=flagretain)
	except:
		print('mqtt send except');


def status(payload):
	mqttsend(statustopic,payload)
	


def command(payload):
	mqttsend(cmdtopic,payload)
	
#grundeinstellung senden
payload = 'stop'
mqttsend(cmdtopic,payload)


#-----------------------------------------------------------------------------------

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
	print(f"mqtt: Connected to {mqttIP} with result code {reason_code}")
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("rover/cmd")
	client.subscribe("rover/test")
	client.subscribe("rover/mapselected")
	
def on_disconnect(client, userdata, rc):
	if rc != 0:
		print("Unexpected MQTT disconnection. Will auto-reconnect")	

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global receiver,test,mapselected
	print('mqtt:',msg.topic+" payload: "+str(msg.payload.decode("utf-8")))	
	if msg.topic == "rover/cmd":
		receiver = str(msg.payload.decode("utf-8"))
	if msg.topic == "rover/test":
		test = str(msg.payload.decode("utf-8"))
	if msg.topic == "rover/mapselected":
		jo = json.loads(msg.payload.decode("utf-8"))
		mapselected = jo
		domap(jo['map'],jo['breite'])
		
##########################################

def domap(mapfile,breite):
	if breite==0:
		return 
	# speichern der Daten 
	# anzeigen der ausgewählten map in der GUI.
	import area
	#print("mapfile",mapfile)
	are = area.loadMap(mapfile,breite/100) # die fläche wird berechnet für furchenabstand
	area.sendmap(are)
	area.resetIst() 

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect

mqttc.connect(mqttIP, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#mqttc.loop_forever()
mqttc.loop_start()

if __name__ == '__main__':
	import time
	payload = 'stop'
	mqttsend(cmdtopic,payload)
	while True:
		time.sleep(0.2)
		

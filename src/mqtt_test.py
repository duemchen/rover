#pip install paho-mqtt  --break-system-packages
#import context  # Ensures paho is in PYTHONPATH

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

mqttIP = "192.168.10.51"
maintopic = 'rover/'
cmdtopic ='cmd'
statustopic = 'status'


receiver = None
test = 199

def getMqttCmd():
	global receiver
	return receiver;
	
def getMqttTest():
	global test
	return test;
	

def mqttsend(utopic,payload):
	try:
		publish.single(maintopic+utopic, payload, hostname = mqttIP)
	except:
		print('mqtt send except');


def status(payload):
	mqttsend(statustopic,payload)
		
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
	
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT disconnection. Will auto-reconnect")	

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global receiver,test
	print('mqtt:',msg.topic+" payload: "+str(msg.payload.decode("utf-8")))	
	if msg.topic == "rover/cmd":
		receiver = str(msg.payload.decode("utf-8"))
	if msg.topic == "rover/test":
		test = str(msg.payload.decode("utf-8"))
		

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
	payload = 'stop'
	mqttsend(cmdtopic,payload)

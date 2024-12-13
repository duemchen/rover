import mqtt_test
import time
from logconfig import log
#import gps_thread_LatLonFix
#import starter
#import offset
import async_bearing
#from position import Position,RoverStatic,RoverDynamic
import basisstation
import antrieb_i2c as antrieb
from enviro import Environment
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqclient
import json

class Joy:

	def __init__(self):				
		self.logger = log
		self.logger.info('Joy instance created')
		
	def joy(self):
		global antr,gturn,gmotor
		async_bearing.setbearingLenkung(False)
		antr = antrieb.Antrieb()
		gturn = 0
		gmotor = 0
		def on_connect(client, userdata, flags, reason_code, properties):
			print(f"mqtt: Connected  with result code {reason_code}")
			# Subscribing in on_connect() means that if we lose the connection and
			# reconnect then subscriptions will be renewed.
			client.subscribe("rover/joy")
		def on_disconnect(client, userdata, rc):
			if rc != 0:
				print("Unexpected MQTT disconnection. Will auto-reconnect")	
		def on_message(client, userdata, message):
			global antr,gturn,gmotor
			#print("%s %s" % (message.topic, message.payload))
			jo = json.loads(message.payload)
			#print(jo['turn'], jo['motor'])
			
			antr.setSpeed(jo['motor'])		#stop wenn keine sollwerte kommen vom gps
			antr.setTurn(jo['turn'])
			gturn = jo['turn']
			gmotor = jo['motor']
			# it's possible to stop the program by disconnecting
			#client.disconnect()
	
		# topic joy lesen
		# direct in turn und speed weitergeben
		# oder den winkel einnehmen und regeln per bearing	
		mqttIP = "192.168.10.51"
		mqttPort = 1883
		mqttcl = mqclient.Client(mqclient.CallbackAPIVersion.VERSION2)
		mqttcl.on_connect = on_connect
		mqttcl.on_message = on_message
		mqttcl.on_disconnect = on_disconnect
		mqttcl.connect(mqttIP, mqttPort, 60)
		mqttcl.loop_start()
		print('fffirst gturn',gturn)
		#subscribe.callback(on_message_print, "rover/joy", hostname=mqttIP,port=mqttPort,userdata={"message_count": 0})	
		print('first gturn',gturn)
		while True:
			time.sleep(0.3)
			antr.setSpeed(gmotor)		#stop wenn keine sollwerte kommen vom gps
			antr.setTurn(gturn)
			print('gturn',gturn,gmotor)
			cmd=mqtt_test.getMqttCmd()
			if(cmd!='joy'):
				break
				antrieb.speed = 0
			#async_bearing.setSollWinkel(alpha,fahrtrichtung) # hier wird per compass schnell und genau eine richtung geregelt
		antrieb.speed = 0
		antr.setSpeed(0)
		antr.setTurn(0)
		mqttcl.unsubscribe("rover/joy")
		mqttcl.loop_stop()
		del mqttcl
		del antr
		async_bearing.setbearingLenkung(True)
		print('driver joy end.')

	

if __name__ == '__main__':
	
	mqtt_test.mqttsend('cmd','dummy')
	env = Environment()
	env.startInnen()	
	joy = Joy()
	joy.joy()
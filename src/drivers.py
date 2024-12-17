import mqtt_test
import time
from logconfig import log
import area
import gps_thread_LatLonFix
import starter
import offset
import async_bearing
from position import Position,RoverStatic,RoverDynamic
import basisstation
import antrieb_i2c as antrieb
from enviro import Environment
import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqclient
import json
import mapposition

class Driver:

	def __init__(self):
		
		self.blinker= time.time()
		self.logger = log
		self.logger.info('Driver instance created')
		self.loadArea()
		#self.loadRechteck()
		
	def loadArea(self):	
		mqtt_test.status('load Area...')		
		jo = mqtt_test.getMapSelected()
		if jo==None:
			jo = json.loads('{"breite": 6,"map": "/home/pi/.rover/mitte.map.json"}')
		map = jo['map']
		breite = jo['breite']
		if breite !=0:
			self.are = area.loadMap(map,breite/100) # die fläche wird berechnet für furchenabstand
			area.sendmap(self.are)
			area.resetIst() 
		else:
			print('driver.loadarea, Fehler: breite=0')
		
	def loadRechteck(self):
		are = area.prepare()
		are.mapnow(a,alpha) #die map wird gebaut in fahrtrichtung und rechts
		area.sendmap(are)
		area.resetIst() #
		
	def blink(self):		
		result = time.time() - self.blinker
		result = round(result,2) #int(result+0.5)
		self.blinker = time.time()
		return str(result)
		
	def start(self):
		self.sendMaplist()
		idx = mapposition.setArePosWeiter(self.are) # ggf. wird an dem idx hier die Fahrt fortgesetzt		
		if idx==-1:
			a = gps_thread_LatLonFix.getRoverPosition() #die aktuelle Position
			if a.fix > 0:
				area.addIstAndSend(a)
				self.are.addAktPos(a)  #von hier zum start 
		a,b = self.are.getNextSectionEinzel()
		
		
		print('erster FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))
		rd = RoverDynamic()
		while True:
			gps_thread_LatLonFix.event.wait(10)
			gps_thread_LatLonFix.event.clear()	
			cmd=mqtt_test.getMqttCmd()
			r = gps_thread_LatLonFix.getRoverPosition() 
			if(cmd=='stop'):
				break
			if r.fix == 0:
				print('no fix.')	
				antrieb.speed = 0		
				continue				
			#GPS hat neue Position gelesen			
			mqtt_test.mqttsend('gps',basisstation.getPositionJson(r))	
			area.addIstAndSend(r)
			rs = RoverStatic(a,b,r)		
			if (rs.getRestweg() < 0.20):
				antrieb.setSlow(7,antrieb.SLOWSPEED)
				# nächsten FahrtAbschnitt einspielen
				rd = RoverDynamic()
				#fahrtrichtung = not fahrtrichtung
				#a,b = are.getNextSectionPaar() 
				a,b = self.are.getNextSectionEinzel()				
				if a==None or b==None:
					print('Ziel erreicht.')
					if not True:
						self.are.reset() #break	
						a,b = self.are.getNextSectionEinzel()
					else:
						break
				print('neuer FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))
				mapposition.saveAktSection(a,b)
			# Action
			if(cmd!='stop'):
				print('Rover moves'+ basisstation.getPositionJson(r))
				mqtt_test.status(self.blink()+',    x='+ str(r.x)+', y='+ str(r.y))
				if (rs.getRestweg() < 0.40):
					antrieb.speed = antrieb.SLOWSPEED
				else : 
					antrieb.speed = antrieb.NORMALSPEED		
			#print('speed',antrieb.speed)
			fahrtrichtung = True
			alpha = rd.getLenkrichtungDynamisch(rs) # hier wird per gps die cm-genaue absolute istbewegung gemessen und daraus der neue sollwinkel berechnet
			async_bearing.setSollWinkel(alpha,fahrtrichtung) # hier wird per compass schnell und genau eine richtung geregelt
		antrieb.speed = 0	
		print('driver end.')
		


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
		mqttcl.unsubscribe("rover/joy")
		#del mqttcl
		async_bearing.setbearingLenkung(True)
		print('driver joy end.')

	def sendMaplist(self):
		import glob
		import os
		from pathlib import PurePosixPath
		from operator import itemgetter
		s = glob.glob("/home/pi/.rover/*.map.json")
		liste = []
		for x in s:
			p = PurePosixPath(x).stem
			p = PurePosixPath(p).stem			
			item = {'label': p, 'value': x}			
			liste.append(item)
		#nach namen sort
		jliste = json.dumps(liste, sort_keys=True, indent=2)
		data_list = json.loads(jliste)
		jliste = json.dumps(sorted(data_list, key=itemgetter('label')))
		print(jliste)
		result = jliste
		mqtt_test.mqttsend('maplist', result, True)			

if __name__ == '__main__':
	
	mqtt_test.mqttsend('cmd','dummy')
	env = Environment()
	env.startInnen()	
	driver = Driver()
	#driver.joy()
	#driver.start()
	driver.sendMaplist()
	while True:
		a,b = driver.are.getNextSectionEinzel()
		print('erster FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))				
		time.sleep(3)
		
	
	
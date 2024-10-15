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

class Driver:

	def __init__(self):
		self.logger = log
		self.logger.info('Driver instance created')
		self.loadArea()
		
	def loadArea(self):	
		mqtt_test.status('load Area...')
		self.are = area.loadMap('einfahrt_zweirad.json',0.30) # die fläche wird berechnet für furchenabstand
		area.sendmap(self.are)
		area.resetIst() #
		
	def start(self):
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
			# Action
			if(cmd!='stop'):
				print('Rover moves'+ basisstation.getPositionJson(r))
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
		
		

if __name__ == '__main__':
	
	mqtt_test.mqttsend('cmd','dummy')
	env = Environment()
	driver = Driver()
	driver.start()
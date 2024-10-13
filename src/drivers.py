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

class Driver:

	def __init__(self):
		self.logger = log
		self.logger.info('Driver instance created')
		self.loadArea()
		self.waitingForFix()
		self.calibrateCompass()
		self.startBearing()

	def loadArea(self):	
		mqtt_test.status('load Area...')
		self.are = area.loadMap('einfahrt_zweirad.json',0.30) # die fläche wird berechnet für furchenabstand
		area.sendmap(self.are)
		area.resetIst() #
		
	def waitingForFix(self):
		gps_thread_LatLonFix.startGPS()
		time.sleep(2)
		#zuerst offset bestimmen
		i=0
		while True:
			cmd=mqtt_test.getMqttCmd()
			if(cmd=='stop'):
				print('Abbruch waitingForFix')
				break;
			gps_thread_LatLonFix.event.wait(10)
			gps_thread_LatLonFix.event.clear()
			a = gps_thread_LatLonFix.getRoverPosition() 	
			if a.fix == 0:
				print('no fix.', i)
				mqtt_test.status('GPS waiting for fix.. '+str(i))
				i+=1
				continue
			break;	
		print('waitingForFix ready')	
		
	def calibrateCompass(self):
		mqtt_test.status('calibrate Compass...')
		ofs=0
		winkelGPS=0
		ofs, winkelGPS = starter.getwinkeloffset() # 1 m fahren zwecks richtung
		offset.writeOffset(ofs) #offset eintragen in ini für position (oder alternativ bearing)
		print('offset',ofs)
		print('winkelGPS',winkelGPS )
		mqtt_test.status('Compass offset '+ str(ofs))
		alpha = winkelGPS
		
	def startBearing(self):
		mqtt_test.status('start Bearing...')
		async_bearing.startbearing() #erst nach calibrierung starten
		
	def start(self):
		a = gps_thread_LatLonFix.getRoverPosition() #die aktuelle Position
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
			rs = RoverStatic(a,b,r)		
			mqtt_test.mqttsend('gps',basisstation.getPositionJson(r))						
			if(cmd=='stop'):
				break
			if r.fix == 0:
				print('no fix.')	
				antrieb.speed = 0		
				continue				
			#GPS hat neue Position gelesen
			area.addIstAndSend(r)
			if (rs.getRestweg() < 0.20):
				antrieb.setSlow(7,antrieb.SLOWSPEED)
				# nächsten FahrtAbschnitt einspielen
				rd = RoverDynamic()
				#fahrtrichtung = not fahrtrichtung
				#a,b = are.getNextSectionPaar() 
				a,b = are.getNextSectionEinzel()
				if a==None or b==None:
					print('Ziel erreicht.')
					if not True:
						are.reset() #break	
						a,b = are.getNextSectionEinzel()
					else:
						break
				print('neuer FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))
			# Action
			print('Rover moves'+ basisstation.getPositionJson(r))
			if (rs.getRestweg() < 0.40):
				antrieb.speed = antrieb.SLOWSPEED
			else : 
				antrieb.speed = antrieb.NORMALSPEED		
			print('speed',antrieb.speed)
			fahrtrichtung = True
			alpha = rd.getLenkrichtungDynamisch(rs) # hier wird per gps die cm-genaue absolute istbewegung gemessen und daraus der neue sollwinkel berechnet
			async_bearing.setSollWinkel(alpha,fahrtrichtung) # hier wird per compass schnell und genau eine richtung geregelt
		print('driver end.')
		
		

if __name__ == '__main__':
	
	mqtt_test.mqttsend('cmd','dummy')
	driver = Driver()
	driver.start()
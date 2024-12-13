import mqtt_test
import time
from logconfig import log
import area
import gps_thread_LatLonFix
#import starter
import offset
import async_bearing
from position import Position,RoverStatic,RoverDynamic
import basisstation
import antrieb_i2c as antrieb
import compass_i2c
import math

class Environment:

	def __init__(self):		
		self.dorun=True
		self.logger = log
		
	def start(self):
		self.logger.info('Umgebung wird gestartet...')
		self.startBearing()
		self.startGpsToFix()
		self.calibrateCompass()
	def startInnen(self):
		self.logger.info('Innen-Umgebung wird gestartet...')
		self.startBearing()
		#self.startGpsToFix()
		#self.calibrateCompass()
		
	
	def stop(self):
		antrieb.speed = 0
		async_bearing.stopbearing() 
		self.dorun=False
		
	def startBearing(self):
		mqtt_test.status('start Bearing...')
		async_bearing.startbearing() 
				
	def startGpsToFix(self):
		mqtt_test.status('start GPS...')
		gps_thread_LatLonFix.startGPS()
		time.sleep(2)
		#zuerst offset bestimmen
		i=0
		while self.dorun:
			time.sleep(0.5)
			cmd=mqtt_test.getMqttCmd()
			if(cmd=='restart'):
				break
			gps_thread_LatLonFix.event.wait(10)
			gps_thread_LatLonFix.event.clear()
			a = gps_thread_LatLonFix.getRoverPosition() 	
			if a.fix == 0:
				print('no fix.', i)
				mqtt_test.status('GPS waiting for fix.. '+str(i))
				i+=1
				continue
			break;	
		print('startGpsToFix ready')	
		return True
		
	def calibrateCompass(self):
		mqtt_test.status('calibrate Compass...')
		ofs=0
		winkelGPS=0
		ofs, winkelGPS = self.getwinkeloffset() # 1 m fahren zwecks richtung
		offset.writeOffset(ofs) #offset eintragen in ini für position (oder alternativ bearing)
		print('offset',ofs)
		print('winkelGPS',winkelGPS )
		mqtt_test.status('Compass offset '+ str(ofs))
		alpha = winkelGPS
		
	def getwinkeloffset(self):	
		a = gps_thread_LatLonFix.getRoverPosition() 
		antrieb.speed = antrieb.SLOWSPEED
		print('speed',antrieb.speed)
		fahrtrichtung = True
		winkelcompass = compass_i2c.bearing16()
		async_bearing.setSollWinkel(winkelcompass,fahrtrichtung)		
		#fahren geradeaus ca. 1m weiter 
		while self.dorun:
			cmd=mqtt_test.getMqttCmd()
			if(cmd=='restart'):
				break
			async_bearing.setSollWinkel(winkelcompass,fahrtrichtung)					
			gps_thread_LatLonFix.event.wait(10)
			gps_thread_LatLonFix.event.clear()
			b = gps_thread_LatLonFix.getRoverPosition() 
			if b.fix == 0:
				print('nofix')
				continue
			weg = math.pow(b.y - a.y , 2) + math.pow(b.x - a.x , 2)
			weg = math.pow(weg, 0.5)
			weg = round(weg,3)
			print('getwinkeloffset Weg:',weg)
			if weg > 1: 
				break
		#motoren.stop()	
		antrieb.speed = 0
		time.sleep(0.2)
		gps_thread_LatLonFix.event.wait(10)
		gps_thread_LatLonFix.event.clear()
		b = gps_thread_LatLonFix.getRoverPosition() 
		# Winkelversatz zwischen GPS und Compass bestimmen
		rs = RoverStatic(a,b,b)
		winkelgps = rs.getLeitstrahlWinkel()
		winkelgps = round(math.degrees(winkelgps),1)
		winkelcompass = compass_i2c.bearing16()
		result = round(winkelcompass - winkelgps,1)
		while result < 0:
			result+=360	#immer positiven Winkel erzeugen
		print('gps:',winkelgps,', compass:',winkelcompass,', result:',result)
		return result,winkelgps

	
	
		
if __name__ == '__main__':
	env = Environment()	      
	print('env ok')
	time.sleep(2)
	env.stop()
	

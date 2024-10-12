import mqtt_test
import time
from logconfig import log
import area
import gps_thread_LatLonFix
import starter
import async_bearing


class Driver:

	def __init__(self):
		self.logger = log		
		self.logger.info('Driver instance created')
		self.loadArea()
		self.waitingForFix()
		self.calibrateCompass()
		self.startBearing()

	def start(self):
		while True:
			cmd=mqtt_test.getMqttCmd()
			if(cmd=='stop'):
				break
			print('drive..')
			time.sleep(1)
		print('driver end.')
		
	def loadArea(self):
		are = area.loadMap('einfahrt_zweirad.json',0.30) # die fläche wird berechnet für furchenabstand
		area.sendmap(are)
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
				i+=1
				continue
			break;	
		print('waitingForFix ready')	
		
	def calibrateCompass(self):
		ofs=0
		winkelGPS=0
		ofs, winkelGPS = starter.getwinkeloffset() # 1 m fahren zwecks richtung
		offset.writeOffset(ofs) #offset eintragen in ini für position (oder alternativ bearing)
		print('offset',ofs)
		print('winkelGPS',winkelGPS )
		alpha = winkelGPS
		
	def startBearing(self):
		async_bearing.startbearing() #erst nach calibrierung starten
		

if __name__ == '__main__':
	
	mqtt_test.mqttsend('cmd','dummy')
	driver = Driver()
	driver.start()
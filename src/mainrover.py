#!/usr/bin/python

#cwd = os.getcwd()  os.chdir

from time import sleep
import logging
import os
import sys
import time
#sys.path.insert(0, 'src')
####sys.path.append(os.path.join(sys.path[0],'src'))
from logconfig import log
import signal
import mqtt_test
from joy import Joy
import setproctitle
from enviro import Environment
from drivers import Driver

#setproctitle.setproctitle('python-rover-main') #setthreadtitle

class MyService:
	def __init__(self, delay=1):
		signal.signal(signal.SIGTERM, self._handle_sigterm)
		signal.signal(signal.SIGINT, self._handle_sigint)
		log.info(sys.version_info)
		self.logger = log
		self.delay = delay
		self.logger.info('MyService instance created')
		self.envi = Environment()  # alle Threads starten 
		
	def start(self):
		mqtt_test.status('Rover program starts')		
		self.envi.start()
		#self.envi.startInnen()
		try:			
			while True:	#in schleife auf mqtt befehle warten, 
						#programmteile anspringen, die ebenfalls von mqtt beendet werden können oder selbst beenden
						#wenn zurück dann status mqtt melden: fertig.
				cmd=mqtt_test.getMqttCmd()
				if(cmd=='start'): 
					driver=Driver()
					driver.start()
				if(cmd=='area'):   # auf seite area wechseln, dort anzeigen der map und berechnung und ggf start
					driver=Driver()
					driver.start()
				if(cmd=='joy'):
					joy=Joy()
					joy.joy()
					del joy
				if(cmd=='restart'):
					print("cmd",cmd) 
					mqtt_test.status('Rover Service Restart')
					os.system("sudo systemctl restart rover.service")
					time.sleep(5)
				mqtt_test.status('Rover is waiting for start')				
				time.sleep(self.delay)
				#x= 3/0
				#raise NameError('HiThere')
				#self.logger.info('Tick')	
		except KeyboardInterrupt:
			self.logger.warning('Keyboard interrupt (SIGINT) received...')
			self.stop()
		'''
		except Exception as err:
			self.logger.warning(f"Unexpected {err=}, {type(err)=}")
			self.stop()
		'''

	def stop(self):
		self.logger.info('Cleaning up...')						
		time.sleep(1)		
		self.envi.stop()
		self.logger.info('bye.')
		#todo was sinnvolles, alle motoren aus.
		mqtt_test.status('Rover Service stop.')		
		time.sleep(0.1)
		sys.exit(0)
		
		
	def _handle_sigterm(self, sig, frame):
		self.logger.warning('MyService SIGTERM received...')
		self.stop()
	def _handle_sigint(self, sig, frame):
		self.logger.warning('MyService SIGINT received...')
		self.stop()



if __name__ == '__main__':
	service = MyService()
	service.start() #am ende der schleife wird das programm verlassen. Oder per SIGINT SIGTERM sofort. 
	#ABER! Danach kann handle was tun!
	log.info('MyService end.')#hier kommen wir nie an
	

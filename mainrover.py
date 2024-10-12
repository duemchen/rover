#!/usr/bin/python

from time import sleep
import logging
import os
import sys
import time
sys.path.insert(0, 'src')
from logconfig import log
import signal
import mqtt_test
from drivers import Driver

class MyService:
	def __init__(self, delay=1):
		signal.signal(signal.SIGTERM, self._handle_sigterm)
		signal.signal(signal.SIGINT, self._handle_sigint)
		log.info(sys.version_info)
		self.logger = log
		self.delay = delay
		self.logger.info('MyService instance created')
		
	def start(self):
		try:			
			while True:	#in schleife auf mqtt befehle warten, 
						#programmteile anspringen, die ebenfalls von mqtt beendet werden können oder selbst beenden
						#wenn zurück dann status mqtt melden: fertig.
				cmd=mqtt_test.getMqttCmd()
				if(cmd=='start'):
					driver=Driver()
					driver.start()
				print('Rover is waiting for start')
				time.sleep(self.delay)
				self.logger.info('Tick')	
		except KeyboardInterrupt:
			self.logger.warning('Keyboard interrupt (SIGINT) received...')
			self.stop()

	def stop(self):
		self.logger.info('Cleaning up...')				
		time.sleep(1)
		self.logger.info('bye.')				
		#todo was sinnvolles, alle motoren aus.
		sys.exit(0)
		
	def _handle_sigterm(self, sig, frame):
		self.logger.warning('SIGTERM received...')
		self.stop()
	def _handle_sigint(self, sig, frame):
		self.logger.warning('SIGINT received...')
		self.stop()



if __name__ == '__main__':
	service = MyService()
	service.start() #am ende der schleife wird das programm verlassen. Oder per SIGINT SIGTERM sofort. ABER! Danach kann handle was tun!
	log.info('end.')#hier kommen wir nie an
	

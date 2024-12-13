#!/usr/bin/env python
import threading
import time
#import mqtt_test
import basisstation
import serial
from position import Position

from serial import Serial
from pyubx2 import UBXReader,UBX_PROTOCOL
import setproctitle
from random import randrange

event = threading.Event()

lat=None
lon=None
fix=None


  
def server_gps(title):	
	"""Simulated function to print server status every 2 seconds."""
	global lat,lon,fix, event
	
	setproctitle.setthreadtitle(title)
	print(title)
	stream = Serial(
		port='/dev/serial0',
		baudrate = 115200,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS,
		timeout=2
	)
	#print('UBX_PROTOCOL',UBX_PROTOCOL) #2
	ubr = UBXReader(stream, protfilter=UBX_PROTOCOL)
	while 1:
		(raw_data, parsed_data) = ubr.read()
		#print(parsed_data)  
		#print("GPS Reader")
		if hasattr(parsed_data, "identity"):
			if parsed_data.identity == "NAV-PVT":
				#print("ident:", parsed_data.identity) 
				lat = parsed_data.lat
				lon = parsed_data.lon
				fix = parsed_data.fixType
				event.set();
				
				
				# die prüfung weglassen und sehen obs geht
				# als ereignis benutzen, um bei jeder neuen nachricht zu lenken
				"""
				if hasattr(parsed_data, "lat"):
					#print('LAT:',parsed_data.lat)
					lat = parsed_data.lat
					#mqtt_test.mqttsend('gps/lat',parsed_data.lat)
					#mqtt_test.mqttsend('gps/dx',basisstation.lat2meter(parsed_data.lat))
				if hasattr(parsed_data, "lon"):
					#print('LON:',parsed_data.lon)
					lon = parsed_data.lon
					#mqtt_test.mqttsend('gps/lon',parsed_data.lon)					
					#mqtt_test.mqttsend('gps/dy',basisstation.lon2meter(parsed_data.lon))
				if hasattr(parsed_data, "xxxgnssFixOK"):
					#print('fix:',parsed_data.gnssFixOK)	  			
					fix = parsed_data.gnssFixOK				
					#mqtt_test.mqttsend('gps',basisstation.getPositionJson(getRoverPosition()))			
				if hasattr(parsed_data, "fixType"):	
					print("fixType", parsed_data.fixType)
					fix = parsed_data.fixType
				"""
	print("stop")
		
	
def startGPS():	
	# Initialize the thread with the server_status function as its target
	t = threading.Thread(target=server_gps,args=('gps',), daemon=True) #'gps'+str(randrange(1000)
	
	
	# Setting the thread as a daemon means it will automatically exit when the main program does
	#t.daemon = True

	# Start the server status thread
	t.start()

def getRoverPosition():
	#lon = basisstation.lon1
	#lat = basisstation.lat1
	#fix = 1
	#print('\n\na',lon,lat,fix)
	return Position(basisstation.lon2meter(lon),basisstation.lat2meter(lat),fix)	
	
def run_server():
	global event
	startGPS()
	time.sleep(2)
	"""Simulated function for server main loop."""
	for _ in range(10):
		# Simulate the server doing some work
		#print("[Server]: Processing data...")
		event.wait()
		event.clear()
		print('run_server:  ', basisstation.getPositionJson(getRoverPosition()))

#run_server()  # Run the main server function
#print("Server shutdown.")
	
	
# pip install pyubx2 --break-system-packages	
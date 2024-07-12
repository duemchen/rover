#!/usr/bin/env python

import time
import serial
from serial import Serial
from pyubx2 import UBXReader


stream = Serial(
	port='/dev/serial0',
	baudrate = 115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
)

ubr = UBXReader(stream, protfilter=2)
while 1:
  (raw_data, parsed_data) = ubr.read()
  #print(parsed_data)
  
  if hasattr(parsed_data, "lat"):
    print('LAT:',parsed_data.lat)
  if hasattr(parsed_data, "lon"):
    print('LON:',parsed_data.lon)
  if hasattr(parsed_data, "gnssFixOK"):
    print('fix:',parsed_data.gnssFixOK)	
  
	
  

	
	
# pip install pyubx2 --break-system-packages	
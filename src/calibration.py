'''
warten auf gps
in 45grd Schritten 2 Vollkreise ausführen 
jeweils 
	vor stop warten auf gps
	zurück stop warten auf gps
möglichst bis Kalibrierung des Sensors auslesen bis 111 erreicht sind.

gps Winkel mit dem Kompass vergleichen.
Diese Winkeldiff für den I-Anteil nutzen.


statt hin her einen kreis fahren bis calibriert
dann eine strecke fahren und winkeloffset bestimmen, ggf. mehrere winkel

'''

import time
import mqtt_test
import voltage
import basisstation
import gps_thread_LatLonFix
from position import Position,RoverStatic,RoverDynamic
import motoren
import compass_i2c
import bearing 
import math
import json


def kreis():
	'''
	rechts rum im Kreis fahren
	stoppen
	cali lesen
	stop wenn calibriert
	'''
	voltage.startVoltage()	
	gps_thread_LatLonFix.startGPS()
	time.sleep(2)
	motoren.setPower(90)
	result = False
	while True:
		print("warten auf fix")
		gps_thread_LatLonFix.event.clear()
		gps_thread_LatLonFix.event.wait(10)
		r = gps_thread_LatLonFix.getRoverPosition() 	
		if r.fix != 0:
			break
	x=20	
	for z in range(3): #3 Runden		
		#break wenn kalib ok.
		cal = compass_i2c.readCalibration()
		sCal = str(bin(cal))
		if sCal[-2:] == "11":
			print("Kompass calibriert")
			result = True
			break			
		motoren.stop()
		time.sleep(0.5)
		motoren.start()		
		motoren.lenke(40,True) #rechts rum Kreis
		time.sleep(x)
		motoren.stop()
	print("Kreis Kalibrierung ", result)

	
def winkeltest():
	'''
	strecke fahren a...b  
	winkel gps mit winkel Kompass vergleichen.
	Das ist der Offset I-Anteil
	'''
	voltage.startVoltage()
	gps_thread_LatLonFix.startGPS()	
	time.sleep(2)
	while True:
		print("warten auf fix")
		gps_thread_LatLonFix.event.clear()
		gps_thread_LatLonFix.event.wait(10)
		r = gps_thread_LatLonFix.getRoverPosition() 	
		if r.fix != 0:
			break	
	motoren.stop()
	time.sleep(0.5)
	gps_thread_LatLonFix.event.clear()
	gps_thread_LatLonFix.event.wait(10)
	a = gps_thread_LatLonFix.getRoverPosition() 
	bearing.startBearing()
	motoren.start()	
	i=180
	bearing.setSollWinkel(i,True)		
	time.sleep(5)
	motoren.stop()
	time.sleep(0.5)
	gps_thread_LatLonFix.event.clear()
	gps_thread_LatLonFix.event.wait(10)
	b = gps_thread_LatLonFix.getRoverPosition() 
	#von a nach b gefahren. Winkel bestimmen.
	r = RoverStatic(a,b,a)		
	gps = math.degrees(r.getLeitstrahlWinkel())
	delta = gps-i
	cal = compass_i2c.readCalibration()
	sCal = str(bin(cal))
	s=toJson(i,gps,delta,sCal)
	print(s)
	mqtt_test.mqttsend("winkeltest",s)
	

def vorrueck():
	voltage.startVoltage()
	bearing.startBearing()
	gps_thread_LatLonFix.startGPS()
	time.sleep(2)
	bearing.startBearing()
	#bearing.setMotor(10)
	#motoren.start()		
	while True:
		print("warten auf fix")
		gps_thread_LatLonFix.event.clear()
		gps_thread_LatLonFix.event.wait(10)
		r = gps_thread_LatLonFix.getRoverPosition() 	
		if r.fix != 0:
			break
	x=3	
	for z in range(3): #3 Runden		
		#break wenn kalib ok.
		cal = compass_i2c.readCalibration()
		sCal = str(bin(cal))
		if sCal[-2:] == "11":
			print("Kompass calibriert")
			break		
		for i in range(0,360,45):
		#for i in [0, 45, 90, 135, 180, 225, 270, 315]:
			print(i , "°")
			motoren.stop()
			time.sleep(0.5)
			gps_thread_LatLonFix.event.clear()
			gps_thread_LatLonFix.event.wait(10)
			a = gps_thread_LatLonFix.getRoverPosition() 
			motoren.start()		
			bearing.setSollWinkel(i,True)			
			time.sleep(x)
			motoren.stop()
			time.sleep(0.5)
			gps_thread_LatLonFix.event.clear()
			gps_thread_LatLonFix.event.wait(10)
			b = gps_thread_LatLonFix.getRoverPosition() 
			#von a nach b gefahren. Winkel bestimmen.
			r = RoverStatic(a,b,a)		
			gps = math.degrees(r.getLeitstrahlWinkel())
			delta = gps-i
			cal = compass_i2c.readCalibration()
			sCal = str(bin(cal))
			s=toJson(i,gps,delta,sCal)
			print(s)
			mqtt_test.mqttsend("calibration",s)
			#rückwärts fahren auf Anfang.
			motoren.start()		
			bearing.setSollWinkel(i+180,False)			
			time.sleep(x)
			motoren.stop()

def toJson(compass,gps,delta, sCal):	
	return json.dumps({"compass": compass, "gps":round(gps,1),"delta": round(delta,1),"sensor":sCal})
		
#vorrueck()
#kreis()
winkeltest()

'''
s = "0b110100"
print(s[-2:])
if s[-2:] == "11":
	print("Kompass calibriert")
'''
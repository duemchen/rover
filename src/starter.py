'''
Rover hinstellen in beliebige Richtung
Rundherum 2m Platz
Wartet auf GPS
Fährt einen Meter vor

Wenn Compass nicht calibriert:
Kreis Durchmesser 1m  zwecks CompassCalibration durchfahren mehrfach

Fährt zurück auf Anfang
Jetzt ist der Versatz zwischen GPS und Compass bekannt und wird benutzt.


Dann zurück auf Startpunkt
Drehung Richtung Startbahn 
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
import sys
import offset


def getwinkeloffset():
	a = gps_thread_LatLonFix.getRoverPosition() 
	motoren.setPower(power)
	motoren.start()	
	motoren.lenke(0,True)
	#fahren geradeaus ca. 1m weiter 
	while True:
		gps_thread_LatLonFix.event.wait(10)
		gps_thread_LatLonFix.event.clear()
		b = gps_thread_LatLonFix.getRoverPosition() 
		weg = math.pow(b.y - a.y , 2) + math.pow(b.x - a.x , 2)
		weg = math.pow(weg, 0.5)
		print('Weg:',weg)
		if weg > 1: 
			break
	motoren.stop()	
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
	print('gps:',winkelgps,', compass:',winkelcompass,', result:',result)
	return result


def kreiscalibierung(a,b):
	#Richtung nun bekannt. Mittelpunkt des Kreises bestimmen, der nun gefahren werden soll. Wir stehen auf der Kreislinie.
	rs = RoverStatic(a,b,b)
	winkel = rs.getLeitstrahlWinkel()
	winkel = round(math.degrees(winkel),1)
	winkel += 90 # kreis rechts in Fahrtrichtung 
	while winkel > 360:
		result -= 360
	dm = 1 #durchmesser
	radius = dm/2
	c = Position(b.x,b.y,True) # aktuelle Position
	c.x += math.sin(math.radians(winkel)) * radius
	c.y -= math.cos(math.radians(winkel)) * radius
	print('Mittelpunkt c: ',c)
	#und jetzt Kreis abfahren solange bis calibriert.
	motoren.start()	
	lenk = 20 #rechts rum anfangsstellung
	schritt = 2 #Änderungsstärke
	motoren.lenke(lenk,True)
	while True:
		gps_thread_LatLonFix.event.wait(10)
		gps_thread_LatLonFix.event.clear()
		d = gps_thread_LatLonFix.getRoverPosition() 
		r = math.pow(d.y - c.y , 2) + math.pow(d.x - c.x , 2)
		r = math.pow(r, 0.5)	
		# immer den richtigen Abstand zum Mittelpunkt anstreben in groben Lenkschritten. ggf. Funktion von Abweichung mit Begrenzungen
		if r>radius:
			lenk += schritt
		else:
			lenk -= schritt
		print('radius:',radius,'rad-ist:',r,'lenk:',lenk)	
		motoren.lenke(lenk,True)
		# abbruch wenn calibriert
		cal = compass_i2c.readCalibration()
		sCal = str(bin(cal))
		if sCal[-2:] == "11":
			print("Kompass calibriert")
			break		

def test():
	global power
	voltage.startVoltage()
	#bearing.startBearing()
	gps_thread_LatLonFix.startGPS()
	time.sleep(2)

	power = 95
	i=0
	while True:
		gps_thread_LatLonFix.event.wait(10)
		gps_thread_LatLonFix.event.clear()
		a = gps_thread_LatLonFix.getRoverPosition() 
		if a.fix == 0:
			print('no fix.', i)			
			i+=1
			continue	
		break;	

	oval=getwinkeloffset() # 1 m fahren zwecks richtung
	offset.writeOffset(oval)
	sys.exit()

	b = gps_thread_LatLonFix.getRoverPosition() 
	kreiscalibierung(a,b) # todo zeitlich limitieren
	#getwinkeloffset()
	#winkel nun hoffentlich stabil für die Fahrt
	#zu a fahren mit bordmitteln, also bearing

	#time.sleep(0.2)
	#sys.exit()

#test()
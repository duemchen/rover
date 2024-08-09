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

voltage.startVoltage()
#bearing.startBearing()
power = 70
gps_thread_LatLonFix.startGPS()
time.sleep(2)
gps_thread_LatLonFix.event.wait(10)
gps_thread_LatLonFix.event.clear()
a = gps_thread_LatLonFix.getRoverPosition() 
motoren.setPower(power)
motoren.start()	
lenke(0,True)
#fahren geradeaus ca. 1m weiter 
while True:
	gps_thread_LatLonFix.event.wait(10)
	gps_thread_LatLonFix.event.clear()
	b = gps_thread_LatLonFix.getRoverPosition() 
	weg = math.pow(b.y - a.y , 2) + math.pow(b.x - a.x , 2)
	weg = math.pow(h, 0.5)
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
winkelcompass = compass_i2c.bearing16()
print('gps:',winkelgps,', compass:',winkelcompass)
#damit könnte man auf Fahrt gehen. Risiko: es calibriert sich irgendwie und ändert sich also plötzlich??


#Richtung nun bekannt. Mittelpunkt des Kreises bestimmen, der nun gefahren werden soll. Wir stehen auf der Kreislinie.
rs = RoverStatic(a,b,b)
winkel = rs.getLeitstrahlWinkel()
winkel += 90 # kreis rechts in Fahrtrichtung 
while winkel > 360:
	result -= 360
dm = 1 #durchmesser
radius = dm/2
c = Position(b.x,b.y,True)
c.x += math.sin(winkel) * radius
c.y -= math.cos(winkel) * radius
print('Mittelpunkt c: ',c)
#und jetzt Kreis abfahren solange bis Calibriert.
motoren.start()	
lenk = 20 #rechts rum anfangsstellung
schritt = 5 #Änderungsstärke
lenke(lenk,True)
while True:
	gps_thread_LatLonFix.event.wait(10)
	gps_thread_LatLonFix.event.clear()
	d = gps_thread_LatLonFix.getRoverPosition() 
	r = math.pow(d.y - c.y , 2) + math.pow(d.x - c.x , 2)
	r = math.pow(r, 0.5)	
	# immer den richtigen Abstand zum Mittelpunkt anstreben in groben Lenkschritten. ggf Funktion von Abweichung mit Begrenzungen
	if r>radius:
		lenk += schritt
	else:
		lenk -= schritt
	lenke(lenk,True)


		

import time
import mqtt_test
#import voltage
import basisstation
import gps_thread_LatLonFix
from position import Position,RoverStatic,RoverDynamic
#import motoren
import antrieb_i2c as antrieb
import compass_i2c
import bearing 
import starter
import offset
import sys
import area

are = area.prepare() # die fläche wird berechnet
area.sendmap(are)
area.resetIst() #
#sys.exit()

#voltage.startVoltage()
#bearing.startBearing() #erst nach calibrierung starten

gps_thread_LatLonFix.startGPS()
time.sleep(2)
#zuerst offset bestimmen
i=0
a = None
while True:
	#print(compass_i2c.readCalibration())
	mqtt_test.mqttsend('compass',compass_i2c.readCalibration())	

	gps_thread_LatLonFix.event.wait(10)
	gps_thread_LatLonFix.event.clear()
	a = gps_thread_LatLonFix.getRoverPosition() 	
	if a.fix == 0:
		print('no fix.', i)			
		i+=1
		#area.addIstAndSend(Position(i,-i,0))
		continue			
	break;	

area.addIstAndSend(a)
A=a
	
#sys.exit()

ofs, winkelGPS = starter.getwinkeloffset() # 1 m fahren zwecks richtung
offset.writeOffset(ofs) #offset eintragen in ini für bearing oder position
print('ofs',ofs)
print('winkelGPS',winkelGPS )
alpha = winkelGPS
are.mapnow(a,alpha)
area.sendmap(are)

#time.sleep(1)
#sys.exit()

#offset ist der I-Regler Anfangswert, der weiter angepasste werden muss, falls der compass umcalibriert !!!
b = a # die erste Startposition wird der neue Zielpunkt
a = gps_thread_LatLonFix.getRoverPosition() #die aktuelle Position
area.addIstAndSend(a)
#offset ende
bearing.startBearing() #erst nach calibrierung starten
rd = RoverDynamic()

#b = are.getFirstPoint() # zum Startpunkt der Fläche

#time.sleep(1)
#sys.exit()

mqtt_test.mqttsend('cmd','start')
fahrtrichtung = True 
# bei nextsectionPaar fahrtrichtung = False #rückwärts zum ErstStartPunkt 
a,b = are.getNextSectionEinzel()
while True:
	#time.sleep(0.5)
	mqtt_test.mqttsend('compass',compass_i2c.readCalibration())	
	gps_thread_LatLonFix.event.wait(10)
	gps_thread_LatLonFix.event.clear()	
	cmd=mqtt_test.getMqttCmd()
	r = gps_thread_LatLonFix.getRoverPosition() 
	rs = RoverStatic(a,b,r)		
	mqtt_test.mqttsend('gps',basisstation.getPositionJson(r))	
	if(cmd!='start'):
		print('Rover stop')
		antrieb.speed = 0
		continue
	if r.fix == 0:
		print('no fix.')	
		antrieb.speed = 0		
		continue
	#GPS hat neue Position gelesen
	area.addIstAndSend(r)
	if (rs.getRestweg() < 0.20):
		antrieb.setSlow(5,50)
		# nächsten FahrtAbschnitt einspielen
		rd = RoverDynamic()
		#fahrtrichtung = not fahrtrichtung
		#a,b = are.getNextSectionPaar() 
		a,b = are.getNextSectionEinzel()
		if a==None or b==None:
			print('Ziel erreicht.')
			if True:
				are.reset() #break	
				a,b = are.getNextSectionEinzel()
			else:
				break
		print('neuer FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))
		# warum? continue
	# Action
	print('Rover moves'+ basisstation.getPositionJson(r))
	if (rs.getRestweg() < 0.30):
		antrieb.speed = 50
	else 
		antrieb.speed = 127		
	alpha = rd.getLenkrichtungDynamisch(rs) # hier wird per gps die cm-genaue absolute istbewegung gemessen und daraus der neue sollwinkel berechnet
	bearing.setSollWinkel(alpha,fahrtrichtung) # hier wird per compass schnell und genau eine richtung geregelt
	
	
		
		

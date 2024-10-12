import time
import mqtt_test
#import voltage
import basisstation
import gps_thread_LatLonFix
from position import Position,RoverStatic,RoverDynamic
#import motoren
import antrieb_i2c as antrieb
import compass_i2c
import async_bearing 
import starter
import offset
import sys
import area

are = area.loadMap('einfahrt_zweirad.json',0.30) # die fläche wird berechnet für furchenabstand
#are = area.readmap('gerade.json') #einfach diese map
area.sendmap(are)
#area.sendsimplemap(are)
area.resetIst() #

#time.sleep(1)
#sys.exit()

gps_thread_LatLonFix.startGPS()
time.sleep(2)
#zuerst offset bestimmen
i=0
a = None
while True:
	cmd=mqtt_test.getMqttCmd()
	if(cmd!='start'):
		print('Rover is waiting for start')
		time.sleep(1)
		continue
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

ofs=0
winkelGPS=0
ofs, winkelGPS = starter.getwinkeloffset() # 1 m fahren zwecks richtung
offset.writeOffset(ofs) #offset eintragen in ini für position (oder alternativ bearing)
print('offset',ofs)
print('winkelGPS',winkelGPS )
alpha = winkelGPS
#
#are.mapnow(a,alpha) #die map wird gebaut in fahrtrichtung und rechts
#area.sendmap(are)
#
#time.sleep(1)
#sys.exit()

a = gps_thread_LatLonFix.getRoverPosition() #die aktuelle Position
area.addIstAndSend(a)
#offset ende
async_bearing.startbearing() #erst nach calibrierung starten
#time.sleep(1)
#sys.exit()
fahrtrichtung = True
antrieb.speed = 0 
async_bearing.setSollWinkel(alpha,fahrtrichtung)
#mqtt_test.mqttsend('cmd','start')
#mqtt_test.mqttsend('cmd','stop')
# bei nextsectionPaar fahrtrichtung = False #rückwärts zum ErstStartPunkt 
are.addAktPos(a)  #von hier zum start
a,b = are.getNextSectionEinzel()
print('erster FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))
rd = RoverDynamic()
while True:
	#time.sleep(0.5)
	#mqtt_test.mqttsend('compass',compass_i2c.readCalibration())	
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
		antrieb.setSlow(7,antrieb.SLOWSPEED)
		# nächsten FahrtAbschnitt einspielen
		rd = RoverDynamic()
		#fahrtrichtung = not fahrtrichtung
		#a,b = are.getNextSectionPaar() 
		a,b = are.getNextSectionEinzel()
		if a==None or b==None:
			print('Ziel erreicht.')
			if not True:
				are.reset() #break	
				a,b = are.getNextSectionEinzel()
			else:
				break
		print('neuer FahrtAbschnitt von','{: >6}'.format(a.x),'{: >6}'.format(a.y),'nach','{: >6}'.format(b.x),'{: >6}'.format(b.y))
		# warum? continue
	# Action
	print('Rover moves'+ basisstation.getPositionJson(r))
	if (rs.getRestweg() < 0.40):
		antrieb.speed = antrieb.SLOWSPEED
	else : 
		antrieb.speed = antrieb.NORMALSPEED		
	print('speed',antrieb.speed)
	alpha = rd.getLenkrichtungDynamisch(rs) # hier wird per gps die cm-genaue absolute istbewegung gemessen und daraus der neue sollwinkel berechnet
	async_bearing.setSollWinkel(alpha,fahrtrichtung) # hier wird per compass schnell und genau eine richtung geregelt
	
	
		
		

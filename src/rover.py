import time
import mqtt_test
import voltage
import basisstation
import gps_thread_LatLonFix
from position import Position,RoverStatic,RoverDynamic
import motoren
import compass_i2c
import bearing 
import starter
import offset
import sys

voltage.startVoltage()
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
		continue	
	break;	
#sys.exit()	
ofs=starter.getwinkeloffset() # 1 m fahren zwecks richtung
offset.writeOffset(ofs) #offset eintragen in ini für bearing oder position
#offset ist der I-Regler Anfangswert, der weiter angepasste werden muss, falls der compass umcalibriert !!!
b = a # die erste Startposition wird der neue Zielpunkt
a = gps_thread_LatLonFix.getRoverPosition() #die aktuelle Position
#sys.exit()
#offset ende
bearing.startBearing() #erst nach calibrierung starten
#a = Position(3.31,-31.5,1)	  
#b = Position(-0.24,-41.33,1)
rd = RoverDynamic()
motoren.stop()
mqtt_test.mqttsend('cmd','start')
fahrtrichtung = True 
fahrtrichtung = False #rückwärts zum ErstStartPunkt 
while True:
	#time.sleep(0.5)
	mqtt_test.mqttsend('compass',compass_i2c.readCalibration())	
	gps_thread_LatLonFix.event.wait(10)
	gps_thread_LatLonFix.event.clear()
	#print("Analog Value: ", channel.value, "Voltage: ", channel.voltage)
	cmd=mqtt_test.getMqttCmd()
	r = gps_thread_LatLonFix.getRoverPosition() 
	rs = RoverStatic(a,b,r)	
	#mqtt_test.mqttsend('istwinkel', round(compass_i2c.bearing16(),1))	
	mqtt_test.mqttsend('gps',basisstation.getPositionJson(r))	
	if(cmd!='start'):
		print('Rover stop')
		motoren.stop()
		continue
	
	
	if r.fix == 0:
		print('no fix.')	
		motoren.stop()
		continue	
	if (rs.getRestweg() < 0.10):
		# nächsten FahrtAbschnitt einspielen
		print('wenden.')	
		motoren.stop()
		x=a
		a=b
		b=x
		rd = RoverDynamic()
		fahrtrichtung = not fahrtrichtung
		continue
	# Action
	print('Rover moves'+ basisstation.getPositionJson(r))
	#motoren.setForward()
	motoren.setPower(95)
	motoren.start()	
	#v = rs.getLenkrichtung()
	alpha = rd.getLenkrichtungDynamisch(rs) # hier wird per gps die cm-genaue absolute istbewegung gemessen und daraus der neue sollwinkel berechnet
	bearing.setSollWinkel(alpha,fahrtrichtung) # hier wird per compass schnell und genau eine richtung geregelt
	
	
		
		

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
bearing.startBearing()

gps_thread_LatLonFix.startGPS()
time.sleep(2)


# 
# Loop to read the analog input continuously



a = Position(3.31,-31.5,1)	  
b = Position(-0.24,-41.33,1)
rd = RoverDynamic()
motoren.stop()
mqtt_test.mqttsend('cmd','start')

fahrtrichtung = True 
while True:
	#time.sleep(0.5)
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
	motoren.setPower(90)
	motoren.start()	
	#v = rs.getLenkrichtung()
	alpha = rd.getLenkrichtungDynamisch(rs)
	bearing.setSollWinkel(alpha,fahrtrichtung)
	
	
		
		

from position import Position,RoverStatic,RoverDynamic
import compass_i2c
import math
import time
import mqtt_test
#import motoren 
import antrieb_i2c as antrieb
import threading
import json  
#import voltage
#import offset


#bus = None
#i2c_address = 0x60
P_FAKTOR = 1  	#1 grad bringt 2% Motordiff (je +-1)
soll = 0		# sollwinkel, der vom Kompass geregelt wird. 
#(GPS stellt ihn nach Leitwinkel und Offset,
#sodass Probleme der Calibrierung des Kompass mit ausgeregelt wird

#compass_i2c.readCalibration()
'''
a = Position(3.31,-31.5,1)	  
b = Position(-0.24,-41.33,1)
r = Position(3.31,-31.5,1)	  #startpos
rs = RoverStatic(a,b,r)
soll = rs.getLeitstrahlWinkel()
soll = round(math.degrees(soll),1) 
'''

def setSollWinkel(so,fr): 
	'''
	Sollwinkel aus den gps Messungen.
	'''
	global soll,fahrtrichtung
	fahrtrichtung = fr
	if fahrtrichtung:
		soll = so
	else:	
		so = so + 180  # ziel mit hinten anvisieren, also um 180 grad gedreht
		while so >= 360: #wenn er positiv ist
			so -= 360
		while so < 0: #wenn er negativ ist
			so += 360
		soll = so
	
def setMotor(v):
	motoren.setForward()
	power = v
	power = min(100,power)
	power = max(0,power)
	motoren.setPower(power)	
	
def getBearingJson(soll, ist, delta):
		return json.dumps({"soll": round(soll,1),"ist": round(ist,1),"delta": round(delta,1)})
			
			
startzeit = None
minzeit = 100
maxzeit = 0
mitzeit = None
			
def zeitmessung():
	global startzeit,minzeit,maxzeit,mitzeit
	if startzeit==None:
		startzeit = time.perf_counter()
		return
	endzeit = time.perf_counter()
	dauer = endzeit-startzeit
	startzeit = endzeit
	minzeit = min(minzeit,dauer)
	maxzeit = max(maxzeit,dauer)
	umfang = 100
	if mitzeit==None:
		mitzeit = dauer
	mitzeit = (umfang * mitzeit + dauer)/(umfang+1)
	
def getZeitmessungJson():
	global minzeit,maxzeit,mitzeit
	if mitzeit != None:  
		return json.dumps({"mittel": round(mitzeit,2),"min": round(minzeit,2),"max": round(maxzeit,2)})

nexttimeBearing = 0
nexttimeVoltage = 0
	
def server_bearing():
	global soll,fahrtrichtung,nexttimeBearing,nexttimeVoltage
	fahrtrichtung = True  # vorwärts true
	drive = antrieb.Antrieb()
	#motoren.stop()
	#offsetwinkel = offset.readOffset()
	#print('bearing.offsetwinkel:', offsetwinkel)	
	while True:
		zeitmessung()
		startzeit = time.perf_counter()	
		time.sleep(0.1)
		ist = compass_i2c.bearing16()
		#ist += offsetwinkel
		#while ist >= 360: #wenn er positiv ist
		#	ist -= 360
		#while ist < 0: #wenn er negativ ist
		#	ist += 360
		ist = round(ist,1)
		'''
		normal immer nur den kleineren dreh wählen, also immer unter 180
		'''
		delta = ist - soll
		if delta > 180:
			delta -= 360
		if delta < -180:
			delta += 360
		delta = round(delta,1)
		# delta positiv zu weit rechts (also nach links lenken)
		delta *= P_FAKTOR
		delta = round(delta,1)
		drive.lenke(-delta,fahrtrichtung)
		#entlastende seltene Aktionen
		if(time.time() > nexttimeBearing):
			mqtt_test.mqttsend('bearing', getBearingJson(soll,ist,delta))			
			nexttimeBearing = time.time() + 3
		if(time.time() > nexttimeVoltage):
			nexttimeVoltage = time.time() + 6
			mqtt_test.mqttsend('voltage', drive.getVoltage())
			mqtt_test.mqttsend('bearingTiming',getZeitmessungJson())

def startBearing():
	# Initialize the thread with the server_status function as its target
	t = threading.Thread(target=server_bearing)
	# Setting the thread as a daemon means it will automatically exit when the main program does
	t.daemon = True
	# Start the server status thread
	t.start()
	
def run_server():
	voltage.startVoltage()
	fahrtrichtung = not True
	setSollWinkel(199,fahrtrichtung)
	startBearing()
	setMotor(90)
	motoren.start()	
	
	"""Simulated function for server main loop."""
	y = None
	while True:
		x = mqtt_test.getMqttTest()
		if x != y:
			y=x
			print('neu ',x)
			setSollWinkel(int(x),fahrtrichtung)			
		time.sleep(0.1)

def run_vorrueck():
	#voltage.startVoltage()
	fahrtrichtung = True
	setSollWinkel(199,fahrtrichtung)
	startBearing()
	#setMotor(90)
	#motoren.start()	
	#antrieb.speed=127
	print(antrieb.speed) 
	
	"""Simulated function for server main loop."""
	x=5
	y=0
	while True:
		print(y)
		setSollWinkel(y,True)			
		time.sleep(x)
		setSollWinkel(y+180,False)			
		time.sleep(x)
		y += 45

def run_drehen():
	vor = not True
	print(antrieb.speed) 
	antrieb.speed = 2
	print(antrieb.speed) 
	startBearing()
	x=7	
	setSollWinkel(0,True)
	time.sleep(x)	
	winkel = [0,170,270,170,0]
	for y in winkel:			
		print(y)
		setSollWinkel(y,vor)
		time.sleep(x)
		
if __name__ == "__main__":
	#run_server()
	#run_vorrueck()
	run_drehen()
'''
Lenkung sorgt für die Einhaltung einer Sollrichtung (Himmelsrichtung)
Sollwinkel einhalten, also sehr gerade fahren und sofort reagieren
P Abstand. Lenkungswert nicht fest sondern proportional bis 0 oder negativ
I Langzeit	Mittelwert	addieren constante
D Änderung	Wenn plötzlich die Wirkung der Lenkung einsetzt/nachlässt, 
  diesem Ruck entgegenwirken.


Streckenabfahrt durch (langsame) Anpassung der Sollrichtung auf Basis GPS
Sollrichtung = Leitstrahlrichtung 
Abstand messen, wenn größer/kleiner wird dann anpassen. 
Parallelfahrt anstreben und dem Leitsrahl nähern
P  SollrichtungsDelta setzen: Abstand langsam verkleinern. Proportional
I  Mittelwert Abstand bilden
(D  entfällt. Schnelle Dinge werden oben getan.)


Wende
Umschaltung auf eine neue Sollrichtung 
- scharfe Reaktion wegen sehr großer Sollabweichung (Ketten laufen gegensinnig)
- in Sollrichtung drehen sofort
- neue Sollrichtung erstmals erreicht/geschnitten?
- dann Abstand ausregeln

'''

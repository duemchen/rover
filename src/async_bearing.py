#https://www.geeksforgeeks.org/garbage-collection-python/

import threading
import asyncio
import aiomqtt
import time
#
from position import Position,RoverStatic,RoverDynamic
import compass_i2c
import math
import antrieb_i2c as antrieb
import json  
import gc
 
print("async_bearing")
print ("Garbage collection thresholds:", gc.get_threshold())


mqttIP = "192.168.10.51"
mqttPort = 1883
#globales
P_FAKTOR = 1  	#1 grad bringt 2% Motordiff (je +-1)
soll = 0		# sollwinkel, der vom Kompass geregelt wird. 
lastsolltime=0
fahrtrichtung = True


async def publish_mqtt(client,topic,val):
		await client.publish(topic, payload=val)

		
def setSollWinkel(so,fr): 
	'''
	Sollwinkel aus den gps Messungen.
	'''
	global soll,fahrtrichtung,lastsolltime
	lastsolltime = time.time()
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
	
def getBearingJson(soll, ist, delta):
		return json.dumps({"soll": round(soll,1),"ist": round(ist,1),"delta": round(delta,1)})
			
			
startzeit = None
minzeit = 100
maxzeit = 0
moxzeit = 0
mitzeit = None
			
def zeitmessung():
	global startzeit,minzeit,maxzeit,moxzeit,mitzeit
	if startzeit==None:
		startzeit = time.perf_counter()
		return
	endzeit = time.perf_counter()
	dauer = endzeit-startzeit
	startzeit = endzeit
	minzeit = min(minzeit,dauer)
	maxzeit = max(maxzeit,dauer)
	moxzeit = max(moxzeit,dauer)
	umfang = 100
	if mitzeit==None:
		mitzeit = dauer
		
	mitzeit = (umfang * mitzeit + dauer)/(umfang+1)
	
def getZeitmessungJson():
	global minzeit,maxzeit,moxzeit,mitzeit
	result =""
	if mitzeit != None:  
		result = json.dumps({"mittel": round(mitzeit,2),"min": round(minzeit,2),"max": round(maxzeit,2),"mox": round(moxzeit,2)})
	maxzeit = 0	
	return result

nexttimeBearing = 0
nexttimeVoltage = 0


# main coroutine for the asyncio program
async def bearing_coroutine():
    # run the event loop a whole
	reconnect_interval = 7  # In seconds
	global soll,fahrtrichtung,nexttimeBearing,nexttimeVoltage
	fahrtrichtung = True  # vorwärts true
	drive = antrieb.Antrieb()
	while True:
		try:
			client = aiomqtt.Client(mqttIP,mqttPort) 
			print('bearing while...')
			####
			while True:
				zeitmessung()
				startzeit = time.perf_counter()						
				ist = compass_i2c.bearing16()
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
				drive.lenke(-delta,fahrtrichtung,lastsolltime)
				#entlastende seltene Aktionen
				if(time.time() > nexttimeBearing):
					async with client:
						await publish_mqtt(client,'rover/bearing', getBearingJson(soll,ist,delta))						
					nexttimeBearing = time.time() + 1
				if(time.time() > nexttimeVoltage):
					nexttimeVoltage = time.time() + 10
					async with client:
						await publish_mqtt(client,'rover/voltage', drive.getVoltage())						
						await publish_mqtt(client,'rover/bearingTiming', getZeitmessungJson())						
				# suspend a moment
				#oo = gc.collect()
				#print('gc:', oo)
				await asyncio.sleep(0.2)
		except aiomqtt.MqttError as error:
			print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
			antriebspeed = antrieb.speed
			antrieb.speed = 0
			await asyncio.sleep(reconnect_interval)
			antrieb.speed = antriebspeed
	print("coroutine ende")
	drive.stop()
 
# create a new thread to execute a target coroutine
def startbearing():
	thread = threading.Thread(target=asyncio.run, args=(bearing_coroutine(),))
	thread.daemon = True
	# start the new thread
	thread.start()

	
def run_drehen():
	vor = True
	print('speed',antrieb.speed) 
	antrieb.speed = 2
	print('speed',antrieb.speed) 
	startbearing()
	x=3	
	time.sleep(x)		
	setSollWinkel(0,True)
	time.sleep(x)	
	winkel = [0,170,270,170,0]
	while True:
		oo = gc.collect()
		print('gc:', oo)
		for y in winkel:			
			print(y)
			setSollWinkel(y,vor)
			time.sleep(x)
	
def geradeaus():
	print(antrieb.speed) 
	antrieb.speed = antrieb.SLOWSPEED
	print('speed',antrieb.speed) 
	soll = compass_i2c.bearing16() #die istrichtung fahren
	setSollWinkel(soll,True)			
	startbearing()
	
	x=1	
	time.sleep(x)
	while True:
		print('soll:',soll,'ist:',compass_i2c.bearing16(),'		speed:',antrieb.speed)
		setSollWinkel(soll,True)			
		time.sleep(x)

	
if __name__ == "__main__":
	#run_server()
	#run_vorrueck()
	#run_drehen()
	geradeaus()
	
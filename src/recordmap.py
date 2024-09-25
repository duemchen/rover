import basisstation
import gps_thread_LatLonFix
import antrieb_i2c as antrieb
import time
import json
from position import Position
import mqtt_test
import pprint
'''
Aufzeichnen einer Map
Dateiname Zeitstempel 
alle Punkte als x y Positionen json Datei
Darstellung in der WEB Map, also MQTT

offlinefähig weil lokal gespeichert
Beeper oder LED wäre gut, 
Motor Ruck nach vorn auch gut
sonst mqtt

'''

MAXDELTA = 0.01 #2cm x oder y
COUNTOK = 3
map = None  # datensammler zunächst leer
filename = time.strftime("map-%m%d-%H.%M.json") #'mapdata.json'
print(filename)

def gleicheOrt(a,b):
	global MAXDELTA
	delta = max(abs(a.x - b.x),abs(a.y-b.y))
	print('delta',delta)
	return delta < MAXDELTA

def ruckVorwärts():
	print('ruckVorwärts')
	a = antrieb.Antrieb()
	a.setSpeed(80)
	a.setTurn(0)
	time.sleep(1.0)		
	a.setSpeed(0)	
	time.sleep(0.5)
	
def toMap(r):
	global map, filename
	
	xy=()
	#xy.x = r.x
	#xy.y = r.y
	map.append([r.x,r.y])
	print(map)
	#[[x,y],[xx,yy]]
	json_object = json.dumps(map, indent=4)	
	#pp = pprint.PrettyPrinter(indent=4, width=80, compact=False)
	#json_object = pp.pprint(json_object)
	
	# Writing to file
	print('toMap Filename',filename)
	with open(filename, "w") as outfile:
		outfile.write(json_object)
	


def recorder():
	global map
	gps_thread_LatLonFix.startGPS()
	time.sleep(2)

	map = []
	counter = 0
	lastPos = None
	i=0
	while True:
		gps_thread_LatLonFix.event.wait(10)
		gps_thread_LatLonFix.event.clear()
		r = gps_thread_LatLonFix.getRoverPosition() 
		if r.fix == 0:
			print('no fix.', i)			
			i+=1		
			continue	
		#GPS gültig
		#drei mal die gleiche Stelle (+-2cm), dann speichern
		if lastPos == None:
			lastPos = r
			continue
		if not gleicheOrt(r,lastPos):
			counter = 0
			lastPos = r		
			continue
		#gleiche Stelle	
		counter += 1
		lastPos = r
		if counter == COUNTOK:  #genau einmal speichern
			toMap(r)
			counter=0
			ruckVorwärts()
	# Wegen Ruckvorwärts jetzt schnell nehmen und zum nächsten Punkt abstellenauf
	# Wenn nur Signalpiep oder Licht, dann beliebig auf eine Ortsveränderung warten
	
def readmap(filename):
	with open(filename, 'r') as openfile:
		# Reading from json file
		mappe = json.load(openfile)
		print(mappe)
		result = []
		for i in mappe:
			p=Position(0,0,1)
			p.x = i[0]
			p.y = i[1]
			result.append(p)
		return result


def toPlotlyMap(poslist):
	xx=[]
	yy=[]
	for i in poslist:
		xx.append(i.x)
		yy.append(i.y)
	li = []
	li.append(xx)
	li.append(yy)
	#print('li\n',li)
	result = json.dumps(li)
	return result
	
#test()

def sendplotlymap(poslist):	
	s =  toPlotlyMap(poslist)	
	mqtt_test.mqttsend('map/soll',s)	

def play(filename):
	poslist = readmap(filename)
	sendplotlymap(poslist)	
	for i in poslist:
		print(i.x)
	
	

if __name__ == "__main__":
	#recorder()
	#play('map-0922-19.25.json')
	play('map-einfahrt.json')
	
	
'''	
dateiname mit zeitstempel versehen zwecks...
oder per GUI funktion starten stoppen. und Dateinamen vergeben
'''
"""
https://www.kompf.de/gps/distcalc.html

distance = sqrt(dx * dx + dy * dy)  Pythagoras für Rasenflächen eine Ebene!

mit distance: Entfernung in km 
dx = 71.5 * (lon1 - lon2)
dy = 111.3 * (lat1 - lat2)
lat1, lat2, lon1, lon2: Breite, Länge in Grad
"""



		
"""	
MQTT senden:

"position": {
    "x": 39.79,
    "y": 9.12
  },	
  
  """

import json  
import mqtt_test  

print('basisStation.py\n\n')


lon1 = 12.8944262
lat1 = 53.1064484
dx1  =   3.31
dy1  = -31.5

lon2 = 12.894373449
lat2 = 53.106358806
dx2  = - 0.24
dy2  = -41.33


lon0 = None
lat0 = None
latFaktor = None
lonFaktor = None



def nullstelle(x1,x2,y1,y2):
	return y1 - (x1 * (y2-y1)/(x2-x1))
	
def el2meter(x1,x2,y1,y2):
	return (x2-x1)/(y2-y1)
	
def basisbau():
	global lon0,lat0,lonFaktor,latFaktor,dx1,dy1,dx2,dy2
	print('basisbau') 
	lon0 = nullstelle(dx1,dx2,lon1,lon2)	
	print('lon0 ',lon0)
	lat0 = nullstelle(dy1,dy2,lat1,lat2)	
	print('lat0 ',lat0)

	lonFaktor = el2meter(dx1,dx2,lon1,lon2)
	latFaktor = el2meter(dy1,dy2,lat1,lat2)
	print('faktoren ',lonFaktor,', ',latFaktor)

	dx = round(lonFaktor * (lon1-lon0),2)
	dy = latFaktor * (lat1-lat0)
	print('Eichpunkt ',dx,', ',dy)

	dx = lonFaktor * (lon2-lon0)
	dy = latFaktor * (lat2-lat0)
	print('Eichpunkt ',dx,', ',dy)



def lat2meter(lat):
	global lat0
	if latFaktor == None:
		basisbau()	
	return round(latFaktor * (lat - lat0),2)
	
def lon2meter(lon):
	global lon0
	if lonFaktor == None:
		basisbau()
	return round(lonFaktor * (lon - lon0),2)
	

def getPositionJsonSimple(dx,dy,fix):
   return json.dumps({ "x": dx, "y": dy,"fix": fix})
   
def getPositionJson(pos):
   return json.dumps({ "x": pos.x, "y": pos.y,"fix": pos.fix})

def test():
	dx = lon2meter(lon1)
	dy = lat2meter(lat1)
	print('Punkt1 ',dx,', ',dy)
	dx = lon2meter(lon2)
	dy = lat2meter(lat2)
	print('Punkt2 ',dx,', ',dy)


   

#jsPos = getPositionJson(dx,dy,"x")
#print (jsPos)
	
#mqtt_test.mqttsend('position',jsPos)	
#print('-----------------------\n\n')

	print("lon,lat delta: ",lon2-lon1,",",lat2-lat1)

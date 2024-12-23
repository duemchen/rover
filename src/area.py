'''
Fläche rechteck 4 Punkte
abstand der furchen 
In quer und längs abzuarbeiten 
durch drehung kann jede Schräge auch berechnet werden.
startpunkt definieren, 
letzter endpunkt speichern

aufsetzen auf den letzten Endpunkt starten und bis zum Ende abarbeiten.
optio längs, quer

dazu vorspulen bis startpunkt

schritte
- berechnen der liste der punkte, die nacheinander anzusteuern sind
- vorscannen bis zum startpunbkt
- anfahren Startpunkt auf unbearbeitetem ende am Feldrand, also immer von oben anfangen, weit weg von der ladestation
- zum laden zur ladestation  (weg vomFeldrand zur Ladestation)

konvertieren zu geojson visualisierung
'''

from position import Position
import math
import json
import mqtt_test
import time
import random
import sys
import os
print('area')


def getGeoJson(p):
	liste = []
	for i in p:		        
		a = [i.x,i.y]				
		liste.append(a)
	return json.dumps({"type": "LineString" , "coordinates": liste})


class area:
	def __init__(self, A,B,C,D):
		self.__A = A
		self.__B = B
		self.__C = C
		self.__D = D
		self.__pattern = None #list der punkte in fester reihenfolge
		self.furchenbreite = 0.2
		self.pos = -1
		
	def __str__(self):
		return 'area pos='+str(self.pos)+', patterLen='+str(len(self.__pattern))
		
	def setPos(self,i):
		self.pos = i
	
	def calcPatternGitter(self):
		print('area.calcPattern')
		p = []
		p.append(self.__A)
		p.append(self.__B)
		p.append(self.__C)
		p.append(self.__D)
		p.append(self.__A)
		#p.clear()
		#erstanwendung etwa rechteck, 
		#also längen oben und unten größere teilen durch furchenabstand, runden und kleinere dann anpassen(enger)
		#quer analog
		p.append(Position(1,-1,0))
		p.extend(self.getArea(self.__A,self.__B,self.__D,self.__C)) #die links und rechts miteinander verbinden, querfahrt
		p.extend(self.getArea(self.__C,self.__B,self.__D,self.__A)) #die unten und oben miteinander verbinden, längsfahrt
		p.append(Position(0,0,0))
		p.append(Position(0.5,-1,0))
		self.__pattern = p
		#for i in self.__pattern:			print(i.x,i.y)
		#print('p\n',p)
		#print('geojson\n\n',getGeoJson(p),'\n')

	def calcPatternLang(self):
		print('area.calcPattern')
		p = []
		p.append(self.__A)
		p.append(self.__B)
		p.append(self.__C)
		p.append(self.__D)
		p.append(self.__A)
		p.clear()
		#erstanwendung etwa rechteck, 
		#also längen oben und unten größere teilen durch furchenabstand, runden und kleinere dann anpassen(enger)
		#quer analog
		##p.append(Position(1,-1,0))
		#p.extend(self.getArea(self.__A,self.__B,self.__D,self.__C)) #die links und rechts miteinander verbinden, querfahrt
		p.extend(self.getArea(self.__A,self.__D,self.__B,self.__C)) #die unten und oben miteinander verbinden, längsfahrt
		##p.append(Position(0,0,0))
		##p.append(Position(0.5,-1,0))
		self.__pattern = p
		#for i in self.__pattern:			print(i.x,i.y)
		#print('p\n',p)
		#print('geojson\n\n',getGeoJson(p),'\n')
			
	def calcPatternBreit(self):
		print('area.calcPattern')
		p = []
		p.append(self.__A)
		p.append(self.__B)
		p.append(self.__C)
		p.append(self.__D)
		p.append(self.__A)
		p.clear()
		#erstanwendung etwa rechteck, 
		#also längen oben und unten größere teilen durch furchenabstand, runden und kleinere dann anpassen(enger)
		#quer analog
		#p.append(Position(1,-1,0))
		p.extend(self.getArea(self.__A,self.__B,self.__D,self.__C)) #die links und rechts miteinander verbinden, querfahrt
		#p.extend(self.getArea(self.__C,self.__B,self.__D,self.__A)) #die unten und oben miteinander verbinden, längsfahrt
		#p.append(Position(0,0,0))
		#p.append(Position(0.5,-1,0))
		self.__pattern = p
		#for i in self.__pattern:			print(i.x,i.y)
		#print('p\n',p)
		#print('geojson\n\n',getGeoJson(p),'\n')
			
		
	def setFurchenbreite(self,f):
		self.furchenbreite = f
		
	def getArea(self,a,b,c,d):		
		''' ab und cd sind die beiden gegenüberliegenden linien, die jetzt mit gitterlinien verbunden werden.'''
		al = math.pow(b.y - a.y , 2) + math.pow(b.x - a.x , 2)
		al = math.pow(al, 0.5)
		cl = math.pow(d.y - c.y , 2) + math.pow(d.x - c.x , 2)
		cl = math.pow(cl, 0.5)
		hmax = max(al,cl)
		count = 1+int(hmax/self.furchenbreite)
		print ('count',count)
		#der Abstand oben und unten
		adiff = al/count
		cdiff = cl/count
		print('furchenbreite',self.furchenbreite)
		print('adiff',adiff)
		print('cdiff',cdiff)
		result = []
		bo=True
		for i in range(0,count+1):
			pa=self.getPunktX(a,b,adiff,i)			
			pc=self.getPunktX(c,d,cdiff,i)
			if bo:
				result.append(pa)
				result.append(pc)
			else:
				result.append(pc)
				result.append(pa)
			bo= not bo
			
			#pc = Position()
			# strecken jeweils umdrehen (von oben nach unten, dann daneben von unten nach oben.accaaccaac)
		return result
		
	def getPunktX(self,a,b,diff,i):
		awinkel = math.atan2(b.x - a.x, b.y - a.y)
		return Position(round(a.x + i* diff * math.sin(awinkel),2), round( a.y + i*diff * math.cos(awinkel),2),1)

	def getPattern(self):
		return self.__pattern
		
	def getNextSectionPaar(self):
		''' das nächste Paar '''
		try:
			result = []
			self.pos +=1
			if self.pos > len(self.__pattern)-1:
				return None,None
			result.append(self.__pattern[self.pos])	
			self.pos +=1
			if self.pos > len(self.__pattern)-1:
				return None,None
			result.append(self.__pattern[self.pos])			
			return result[0],result[1]
		finally:
			self.sendMapDoneSoll() #war unten im finally

	def getNextSectionEinzel(self):
		''' letzer Punkt bis zum nächsten '''
		try:
			result = []
			if self.pos == -1:
				self.pos +=1
			if self.pos > len(self.__pattern)-1:
				return None,None
			result.append(self.__pattern[self.pos])	
			self.pos +=1
			if self.pos > len(self.__pattern)-1:
				return None,None
			result.append(self.__pattern[self.pos])			
			return result[0],result[1]
		finally:
			self.sendMapDoneSoll() #war unten im finally
		
	
	def getFirstPoint(self):
		result = self.__pattern[0]
		return result
	def reset(self):
		self.pos = -1
		#self.__pattern[0]
		
	def addAktPos(self,a):
		self.__pattern.insert(0, a)
	
	def setPattern(self,p):
		self.__pattern=p
	
		
		'''
			die punkte sind so in der rechten reihenfolge, der rover muss immer 2 zu einer strecke machen am wendepunkt
			oder das paaren machen wie gleich und geben am wendepunkt die nächste strecke
			bis punkt ... gefahren  laufende nummer der liste
		'''

	def mapnow(self,A,alpha):

		'''
		Fahrzeug in eine Richtung stellen 
		vorne und rechts soll genügend Platz sein!

		Am Startpunkt 1 m fahren zwecks compassOffset
		ABCD berechnen aus Richtung, Länge und Breite
		Dann gleich weiterfahren zum Punkt B,C,D und zurück zu A und das als ist ausgeben
		'''	
		soll = []	
		#
		
		length = 2 #Meter
		width = 1
		#
		
		B = Position(0,0,1)
		B.x = A.x + length * math.cos(math.radians(90-alpha))
		B.y = A.y + length * math.sin(math.radians(90-alpha))	
		D = Position(0,0,1)
		D.x = A.x + width * math.sin(math.radians(90-alpha))
		D.y = A.y - width * math.cos(math.radians(90-alpha))
		C = Position(0,0,1)
		C.x = D.x + length * math.cos(math.radians(90-alpha))
		C.y = D.y + length * math.sin(math.radians(90-alpha))	
		A.round()
		B.round()
		C.round()
		D.round()
		soll.append(A)
		soll.append(B)
		soll.append(C)
		soll.append(D)
		soll.append(A)
		s =  getJsonMap(soll)	
		mqtt_test.mqttsend('map/soll',s)
		self.__pattern.clear()
		self.__pattern.extend(soll)		

	def calcRahmen(self):
		print('area.calcRahmen')  #fehlerhaft
		p = []
		p.append(self.__A)
		p.append(self.__B)
		p.append(self.__C)
		p.append(self.__D)
		p.append(self.__A)
		self.__pattern = p
		print('rahmen',p)
		
	
	def sendMapDoneSoll(self):
		# done und soll an mqtt senden am aktuellen index trennen
		#print(ist)
		list = self.getPattern()
		print("listlen", len(list))
		idx = self.pos
		done = list[:idx+1]
		print("done",len(done))
		s = getJsonMap(done)
		mqtt_test.mqttsend('map/done',s)	
		soll = list[idx:] 		
		print("soll",len(soll))
		s = getJsonMap(soll)
		mqtt_test.mqttsend('map/soll',s)	
		
def prepare():	
	a = Position(3.31-1,-31.5,1)	  
	b = Position(-0.24-1,-41.33,1)
	c = Position(-0.24+1,-41.33,1)
	d = Position(3.31+1,-31.5,1)
	result = area(a,b,c,d)
	result.setFurchenbreite(0.25)
	#result.calcPatternGitter()
	result.calcPatternLang()
	#result.calcPatternBreit()
	p = result.getPattern()
	#print('prepare: geojson\n\n',getGeoJson(p),'\n')
	return result

	
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

	
def loadMap(filename,furchenbreite = 0.5):	
	# nicht als service: poslist = readmap(filename)
	poslist = readmap(os.path.realpath(filename))
	
	for p in poslist:
	  print(p.x,len(poslist))
	a = poslist[0]  
	b = poslist[1]  
	c = poslist[2]  
	d = poslist[3]  
	#sys.exit()
	#a = Position(3.31-1,-31.5,1)	  
	#b = Position(-0.24-1,-41.33,1)
	#c = Position(-0.24+1,-41.33,1)
	#d = Position(3.31+1,-31.5,1)
	result = area(a,b,c,d)
	result.setFurchenbreite(furchenbreite)
	#result.calcPatternGitter()
	result.calcPatternLang()
	#result.calcPatternBreit()
	p = result.getPattern()
	#print('prepare: geojson\n\n',getGeoJson(p),'\n')
	return result

def loadRahmen(filename):	
	poslist = readmap(os.path.realpath(filename))
	
	for p in poslist:
	  print(p.x,len(poslist))
	a = poslist[0]  
	b = poslist[1]  
	c = poslist[2]  
	d = poslist[3]  
	result = area(a,b,c,d)	
	result.calcRahmen()
	

		
def test():
	a = area(Position(0.0,0.0,1),Position(-4.0,10.0,1),Position(12.0,12.0,1),Position(10.0,-2.0,1))
	a.setFurchenbreite(2.5)
	#a.calcPatternGitter()
	a.calcPatternLang()
	#a.calcPatternBreit()
	p = a.getPattern()
	print('geojson\n\n',getGeoJson(p),'\n')
	#die letzte Position wird in datei gespeichert. Ohne reset machen wir da weiter. Mit reset beginnen wir am Anfang
	#a.resetPos() 
	#a.getPosProz()
	#gesamtstrecke, reststrecke prozent
	while True:
		m,n = a.getNextSection()
		if m==None or n==None:
			break
		print(m.x,m.y,n.x,n.y)
		
		
		#if len(ab)<2:
		#	break		
		#print(ab[0].x,ab[0].y,ab[1].x,ab[1].y) #liefert 2 positionen, sie neue Strecke, die abgefahren werden soll
		

		

def getJsonMap(p):
	xx=[]
	yy=[]
	for i in p:
		xx.append(i.x)
		yy.append(i.y)
	li = []
	li.append(xx)
	li.append(yy)
	#print('li\n',li)
	result = json.dumps(li)
	return result
	
#test()

def sendmap(myarea):
	#map = prepare()
	s =  getJsonMap(myarea.getPattern())
	#print('s\n',s)
	mqtt_test.mqttsend('map/soll',s)	
	#arr = json.loads(s)
	#print('loads\n', arr[0])	
	#print('loads\n', arr[1])	
	
	

	
	
	
def sendsimplemap(mp):
	#map = prepare()
	s =  getJsonMap(mp)
	#print('s\n',s)
	mqtt_test.mqttsend('map/soll',s)	
	#arr = json.loads(s)
	#print('loads\n', arr[0])	
	#print('loads\n', arr[1])	
	
	
def resetIst():
	global ist
	ist = []
	#print(ist)
	mqtt_test.mqttsend('map/ist','[[],[]]')	
	
	
def addIstAndSend(pos):
	'''
	die aktueller Roverposition an die Ist anhängen und versenden
	alternativ kann die liste auch 
	auf dem server gebaut und erweitert werden, 
	wenn die Datensendung zu groß ist.
	'''
	ist.append(pos.copy())
	#print(ist)
	s =  getJsonMap(ist)
	#print('s\n',s)
	mqtt_test.mqttsend('map/ist',s)	

	
	
	
def testist():
	resetIst()
	for i in (1,2,3,4,5,6):
		addIstAndSend(Position(random.randint(-1, 4),random.randint(-40, -30),0))
		time.sleep(1)


	
def mapnowtest():
	are = prepare()
	resetIst()
	A =  Position(0.0,0.0,1)
	alpha = 20  #grad
	are.mapnow(A,alpha)
	sendmap(are)
		
		
def testDoneSollIst():
	a = area(Position(0.0,-0.0,1),Position(-4.0,10.0,1),Position(12.0,12.0,1),Position(10.0,-2.0,1))
	a.setFurchenbreite(2.5)
	#a.calcPatternGitter()
	a.calcPatternLang()
	a.setPos(10)
	a.sendMapDoneSoll()
	resetIst()


	
def loadAB(pa,pb):
		are = area(Position(0.0,-0.0,1),Position(-4.0,10.0,1),Position(12.0,12.0,1),Position(10.0,-2.0,1))
		p = []
		p.append(pa)
		p.append(pb)
		are.setPattern(p)
		return are

def sendgpspos(pos):
	s = json.dumps({ "x": pos.x, "y": pos.y,"fix": pos.fix})
	mqtt_test.mqttsend('gps',s)

	
if __name__ == "__main__":
	#testist()
	#mapnowtest()
	#testDoneSollIst()
	
	gpspos = Position(0,0,1)	
	sendgpspos(gpspos)
	resetIst()
	addIstAndSend(gpspos)
	are = loadAB(Position(-50,10,1),Position(50,10,1)) # 	
	are.sendMapDoneSoll()
	sendmap(are)
	
	

	
	
	
		
'''
{
    "type": "LineString",
    "coordinates": [
        [
            -11.744384,
            39.32155
        ],
        [
            -10.552124,
            9.330048
        ]
       ]
}
'''


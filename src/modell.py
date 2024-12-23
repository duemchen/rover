from position import Position, RoverStatic, RoverDynamic
import mqtt_test
import json
import area
import threading
import mapposition
import time
import math
import area

'''
neustart bei jedem gps signal
bis zum neuen gps:
	wenn neuer gps Pos mit zeitstempel und Geschwindigkeit,
	dann diesen Messwet nehmen
	sonst zp der neuen berechnung nehmen,
	mit der geschwindungkeit daraus den neuen punkt berechnen
	
	daraus Abstand und daraus neue lenkrichtung
	
	ggf. Modellkorrektur durch vgl Messung und Berechnung
	
	jedesmal auch Prüfung leitstrahl-Aktualisierung (Routenteilstrecke weiterrücken)
	Restweg mit Motordrosselung an ecken
	
'''
class Poszeit:
	def __init__(self, zeitpunkt, position, winkel):
		self.zeitpunkt=zeitpunkt
		self.position=position
		self.winkel=winkel
	def __str__(self):
		return '[Zeitpkt: '+ str(self.zeitpunkt) + ', Pos:' + str(self.position) + ', Winkel:' + str(self.winkel)+']'
	def copy(self):
		result = Poszeit(0,Position(0,0,0),0)
		result.zeitpunkt=self.zeitpunkt
		result.position=self.position.copy()
		result.winkel = self.winkel
		return result
		
class Modell:
	'''
	hier werden alle Daten gehalten und verrechnet
	'''

	def __init__(self):		
		self.are = None
		#übergabe der neuen gps
		self.gpspoz = Poszeit(0,None,0)
		self.gpsv = 0
		#merken letzte und akt. berechnte pz
		self.pz1 = Poszeit(0,Position(0,0,0),0)
		self.pz2 = Poszeit(0,Position(0,0,0),0)
		#static und dynamic Rover
		self.rs = None
		self.rd = RoverDynamic()
		#aktuelle leitline
		self.a = None 	#leitstrecke
		self.b = None
		#geschwindigkeit
		self.v = 0.1	#m/sec	#geschwindigkeit durch 2 gps bestimmen, dann erst modell aktivieren. bei jedem gps eingang neu setzen/mitteln
		#eventsteuerung. eine neue gps kommt rein
		self.gpsevent = threading.Event()
		self.gpsevent.clear()
		
	def setare(self, are, gpspos):
		self.are=are
		idx = mapposition.setArePosWeiter(self.are) # ggf. wird an dem idx hier die Fahrt fortgesetzt		
		print('setare idx',idx)
		idx = -1
		if idx==-1:
			area.addIstAndSend(gpspos.copy())
			#self.are.addAktPos(gpspos.copy())  #von hier zum start 
		print('are',are,are.pos)
		self.a, self.b = self.are.getNextSectionEinzel()
		print('are',are,are.pos)
		print('setare leitlinie a:',self.a,', b:',self.b)
		
	def calcPos2(self):
		# aus v und Winkel Weg und somit neuen Ort berechnen			
		#print('vor---------------------',self.pz1.zeitpunkt,self.pz2.zeitpunkt)
		self.pz2.zeitpunkt = time.time()
		#print('nach--------------------',self.pz1.zeitpunkt,self.pz2.zeitpunkt)
		zeit = self.pz2.zeitpunkt - self.pz1.zeitpunkt		
		h = self.v * zeit #hypothenuse
		#winkel = (self.pz1.winkel + self.pz2.winkel) / 2  # Mitteln
		winkel = self.pz1.winkel 
		print('calpos2 winkel',winkel,h)
		# p2.position berechnen
		x =  math.sin(math.radians(winkel)) * h
		y =  math.cos(math.radians(winkel)) * h
		print('xy--------pz1 ',self.pz2.zeitpunkt-self.pz1.zeitpunkt,self.v,h,winkel,x,y)
		self.pz2.position.x = self.pz1.position.x + x
		self.pz2.position.y = self.pz1.position.y + y
		
	def calculate(self):
		# entweder eine frische GPS oder eine am Modell berechnete Position
		if self.gpsevent.is_set():
			print('gpsevent-----------------------------')
			self.pz2 = self.gpspoz
			self.v = self.gpsv
			self.gpsevent.clear()
		else:			
			print('calcpos2-----------------------------')
			self.calcPos2()
		area.addIstAndSend(self.pz2.position.copy())
		
	def setgpspoz(self,gpspos,gpstime):
		# von aussen gefüllt
		self.calcvelocity(gpspos,gpstime)
		# neues gps wird zu altem gps für nächste berechnung	
		self.gpspoz.position = gpspos.copy()
		self.gpspoz.zeitpunkt = gpstime
		self.gpspoz.winkel = 180  # winkelmessung zum Zeitpunkt ??		
		self.gpsevent.set() # mitteilung an bearing zur übernahme der neuen position in die simulation
		
	def calcvelocity(self,gpspos,gpstime):
		def pythagoras(c,d):
			result = math.pow(c, 2) + math.pow(d, 2)
			result = math.pow(result, 0.5)
			return result
		if self.gpspoz.position != None:
			a = self.gpspoz.position
			b = gpspos
			self.gpsv = pythagoras((a.x-b.x),(a.y-b.y)) / abs(gpstime - self.gpspoz.zeitpunkt)
			self.v = self.gpsv
		print('velo:',self.v)
		
	def getLenkrichtung(self):
		alpha = self.rd.getLenkrichtungDynamisch(self.rs)
		print('getlenkrichtung',alpha)
		self.pz2.winkel = alpha 
		self.pz1 = self.pz2.copy() #bei nächsten Berechnen der VON-Poz
		print('pz2',self.pz2)
		return alpha
		
	def leitlinie(self):
		print('restweg',self.rs.getRestweg())
		if self.rs.getRestweg() < 0.05:
			print(self.are.pos,' index-----------------------------------')
			self.a, self.b = self.are.getNextSectionEinzel()	#umschaltung zur nächsten Section
			print('leitlinie a:',self.a,', b:',self.b)
		result = not((self.a is None) or (self.b is None)) #abbruchbedingung
		return result
		
	def lenkeviaModell(self):
		self.calculate() #erzeugt den neuen imaginären punkt pz2
		self.rs = RoverStatic(self.a, self.b ,self.pz2.position.copy())
		if not self.leitlinie():
			print('Streckenende erreicht')
			return None			
		alpha = self.getLenkrichtung()
		return alpha
		
	def getGpsRandom(self):
		import random
		result = self.pz2.position.copy()
		delta = 0.5
		result.x += random.uniform(-delta, delta)
		result.y += random.uniform(-delta, delta)
		return result
	
def loadArea():	
	mqtt_test.status('load Area...')		
	jo = mqtt_test.getMapSelected()
	if jo==None:
		jo = json.loads('{"breite": 6,"map": "/home/pi/.rover/mitte.map.json"}')
	map = jo['map']
	breite = jo['breite']
	if breite !=0:
		are = area.loadMap(map,breite/100) # die fläche wird berechnet für furchenabstand
		area.sendmap(are)
		area.resetIst() 
	else:
		print('driver.loadarea, Fehler: breite=0')
	return are	

	
def test():
	
	gpspos = Position(0,0,1)
	#
	area.resetIst()
	area.addIstAndSend(gpspos)
	#
	are = loadArea()  #via mqtt definiert
	#are.addAktPos(gpspos)  #von hier zum start 
	#
	model = Modell()
	model.setare(are,gpspos)			
	model.setgpspoz(gpspos,time.time()) 
	time.sleep(1)
	gpspos = Position(1,1,1)
	model.setgpspoz(gpspos,time.time()) 
	
	i=0
	print('while---------------------------------------------------------')
	while True:		
		i+=1
		print('while',i)
		time.sleep(1)
		alpha = model.lenkeviaModell()
		if alpha == None:
			print('Fahrt ende.')
			break
		print('alpha:', alpha)
		#if i>10:	i=0		model.setgpspoz(pos,time.time())  #generieren gps in der korrekten stelle der leitline mit zufälligen abweichungen
		#if i > 2:			break

def testAB():
	# nur eine Linie zeigen und an der fahren
	are = area.loadAB(Position(50,10,1),Position(-50,5,1)) # 
	area.sendmap(are)
	area.resetIst()
	
	gpspos = Position(0,-2,1)	
	area.sendgpspos(gpspos)
	area.addIstAndSend(gpspos)
	model = Modell()
	model.setare(are,gpspos)			
	time.sleep(1)	
	gpspos = Position(0,-1,1)	
	area.addIstAndSend(gpspos)
	model.setgpspoz(gpspos,time.time()) #
	time.sleep(3)
	gpspos = Position(0,0,1)
	area.addIstAndSend(gpspos)
	model.setgpspoz(gpspos,time.time())
	time.sleep(1)
	# zwei gpspos ergeben eine richtung und geschwindigkeit des rovers
	# der rover muss sich in fahrtrichtung ziel an die leitlinie annähern.
	# er kann zunächst stoppen und dich in sollrichtung drehen
	i=0
	print('while---------------------------------------------------------')
	gpsAlleXSekunden = 1
	nextGps = time.time()+gpsAlleXSekunden
	while True:	
		#break
		i+=1
		print('while',i)
		time.sleep(0.1)		
		alpha = model.lenkeviaModell()
		if alpha == None:
			print('Fahrt ende.')
			break
		print('alpha:', alpha)
		#ab und zu eine gpspos erfinden, kleine Abweichungen per random, Regelung muss darauf aufsetzen
		if time.time()>nextGps:
			nextGps = time.time()+gpsAlleXSekunden
			gpspos = model.getGpsRandom()
			model.setgpspoz(gpspos,time.time())
		
		#if i>20:
		#	break
		
	time.sleep(2)


		
if __name__ == "__main__":
	#test()
	testAB()



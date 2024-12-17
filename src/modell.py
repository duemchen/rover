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
class Poszeit
	def __init__(self, zeitpunkt, position, winkel):
		self.zeitpunkt=zeitpunkt
		self.position=position
		self.winkel=winkel
		
class Modell
	'''
	hier werden alle Daten gehalten und verrechnet
	'''

	def __init__(self):
		are ist die komplette berechnete fahrtroute. die karte hier laden? durch weiterbewegung komme ich an ende der strecke. neuen abschnitt aufrufen
		#
		self.are = None
		#
		self.gpspoz = None
		self.gpsv = 0
		#
		self.pz1 = None
		self.pz2 = None
		#
		self.ps = None
		self.pd = None
		#
		self.a = None 	#leitstrecke
		self.b = None
		#
		self.v = 0		#geschwindigkeit durch 2 gps bestimmen, dann erst modell aktivieren. bei jedem gps eingang neu setzen/mitteln
		self.gpsevent = threading.Event()
		self.gpsevent.clear()
		
	def setare(self, are, gpspos):
		self.are=are
		idx = mapposition.setArePosWeiter(self.are) # ggf. wird an dem idx hier die Fahrt fortgesetzt		
		if idx==-1:
			area.addIstAndSend(gpspos)
			self.are.addAktPos(gpspos)  #von hier zum start 
		self.a, self.b = self.are.getNextSectionEinzel()
		
	def calcPos2(self):
		# aus v und Winkel Weg und somit neuen Ort berechnen	
		self.pz2.zeitpunkt = time.time()
		zeit = self.pz2.zeitpunkt - self.pz1.zeitpunkt		
		h = self.v * zeit #hypothenuse
		winkel = (pz1.winkel + pz2.winkel) / 2  # Mitteln
		# p2.position berechnen
		x =  math.sin(winkel) * h
		y =  math.cos(winkel) * h
		self.pz2.x = self.pz1.position.x + x
		self.pz2.y = self.pz1.position.y + y
		
	def calculate(self):
		# entweder eine frische GPS oder eine am Modell berechnete Position
		if gpsevent.is_set():
			self.p2 = self.gpspoz
			self.v = self.gpsv
			self.gpsevent.clear
		else:
			calcPos2()
		area.addIstAndSend(self.p2.position)
		
	def setgpspoz(self,gpspos,gpstime):
		# von aussen gefüllt
		self.calcvelocity(gpspos,gpstime)
		# neues gps wird zu altem gps für nächste berechnung
		self.gpspoz.position = gpspos
		self.gpspoz.zeitpunkt = gpstime
		#self.gpspoz.winkel = gpswinkel  # winkelmessung zum Zeitpunkt ??		
		self.gpsevent.set() # mitteilung an bearing zur übernahme der neuen position in die simulation
		
	def calcvelocity(gpspos,gpstime)
		def pythagoras(c,d):
			result = math.pow(c, 2) + math.pow(d, 2)
			result = math.pow(result, 0.5)
		if gpspoz <> None:
			a = self.gpspoz.position
			b = gpspos
			self.gpsv = pythagoras((a.position.x-b.position.x),(a.position.y-b.position.y)) / abs(gpstime - a.zeitpunkt)
		print('velo:',self.v)
		
	def getLenkrichtung(self, rs):
		# Am Ende des Leitstrahls zum neuen schalten
		
		alpha = rd.getLenkrichtungDynamisch(rs)
		self.p2.winkel = alpha 
		self.pz1 = self.pz2 #bei nächsten Berechnen der VON-Poz
		return alpha
		
	def leitlinie(self,rs):
		if rs.getRestweg() < 0.20):
			self.a, self.b = self.are.getNextSectionEinzel()	#umschaltung zur nächsten Section
		result = not(self.a=None || self.b==None) #abbruchbedingung
		
	def lenkeviaModell(self):
		model.calculate()
		rs = RoverStatic(a,b,self.p2.position)
		if not model.leitlinie(rs):
			print('Streckenende erreicht)
			break			
		alpha = model.getLenkrichtung(rs)
		return alpha

	
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
		gpspos = Position(0,0,0)
		are = loadArea()  #via mqtt definiert
		model =  Modell()
		model.setare(are,gpspos)		
		i=0
		while True:
			i+=1
			time.sleep(1)
			alpha = model.lenkeviaModell()
			print('alpha:'+ alpha)
			if i>10:
				i=0
				model.setgpspoz(pos,time.time())  #generieren gps in der korrekten stelle der leitline mit zufälligen abweichungen
		
		
		
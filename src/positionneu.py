import math
import mqtt_test

class Position:
	"""Koordinatenpaar lon lat mit fix"""
	def __init__(self, lon, lat, fix):	
		self.x=lon
		self.y=lat
		self.fix=fix
		#print('a: ' + str(self.x) + ', ' + str(self.y)+ ', ' + str(self.fix))
	  
	  
	  
class RoverStatic:
	"""akt. statische Situation des Rover zur akt. StartZielLinie """
	def __init__(self,start, ziel, rover):
		self.__a = start
		self.__b = ziel
		self.__r = rover
		self.__leitstrahlwinkel = 0
		self.__roverzielwinkel =
		self.__delta = 0.0
		self.__rest = 0.0 
		self.calc()
		
		
    def getLeitstrahlWinkel(self):	
		return self.__leitstrahlwinkel
	def getRoverZielWinkel(self):
		return self.__roverzielwinkel
	def getAbstand(self):
		return self.__delta
	def getRestweg(self):
		return self.__rest
	def getRoverPosition(self):
		return self.__r
	def getLenkrichtung(self):
		""" lt. akt. Abstand """
		if self.getAbstand() > 0.05:
			print('links')
			return -1
		elif self.getAbstand() < -0.05:
			print('rechts')
			return 1
		else:	
			print('gerade')
			return 0
		
	 
		
	def calc(self):
		#print("calc----------------------------")
		wsoll = math.atan2(self.__b.y - self.__a.y, self.__b.x - self.__a.x)
		self.__leitstrahlwinkel = wsoll
		wrover = math.atan2(self.__b.y - self.__r.y, self.__b.x - self.__r.x)
		self.__roverzielwinkel = wrover
		#print('wrover',wrover,' ', round(math.degrees(wrover),2),' Grad')

		# Wenn wrover > wsoll muss nach links gelenkt werden.
		# der Abstand von der Sollinie
		#pythagoras
		h = math.pow(self.__b.y - self.__r.y , 2) + math.pow(self.__b.x - self.__r.x , 2)
		h = math.pow(h, 0.5)
		#print('h '+ str(h))

		# Abstand sinus  positiv heisst rechts von soll. also nach links lenken
		self.__delta = round(h * math.sin(wrover - wsoll),2)
		#print('abstand '+ str(self.__delta))
		mqtt_test.mqttsend('abstand',self.__delta)	
		
		# Punkt Lot , ist er noch vor dem Ziel? positiv heisst vor dem ziel 
		self.__rest = round(h * math.cos(wrover - wsoll),2)
		#print('rest '+ str(self.__rest))
		mqtt_test.mqttsend('rest',self.__rest)	
		
		
class RoverDynamic:
	""" dynamischer Zustand des Rovers
	Merken des letzen Abstandes um stärker zu lenken oder bereits gegen zu lenken
	Merken der letzten Position, um die Richtung zu bestimmen
	Takten der Aktualisierung
	"""
	def __init__(self):
		print('RoverDynamic init')
		self.__lastStatic = None	
		
	def getDirection(self, rStatic):
		a = self.__lastStatic.getRoverPosition()
		b = rStatic.getRoverPosition()		
		dir = math.atan2(b.y - a.y, b.x - a.x)
		print('dir:',dir,' ', math.degrees(dir))
		return dir
		
				
	def getLenkrichtungDynamisch(self,rStatic):
	''' das weitergegenlenken wird bei Abstandsverringerung abgebrochn '''
		print('RoverDynamic action')		
		a = self.__lastStatic
		b = rStatic
		if a is None:
			self.__lastStatic = b
			return
		result = b.getLenkrichtung() 	
		dir = self.getDirection(b)
		if (b.getAbstand() < 0) xor (a.getAbstand() < 0):
			# soll-line gekreuzt, gegenlenken wie static.
			result = result
		elif:	
			# normalfall auf einer Seite
			if abs(b.getAbstand()) < abs(a.getAbstand())
				# Abstand wird kleiner. genug gelenkt.
				result = 0
				"""
				# oder weiter gegenlenken, aber nicht steiler als  45 grad auf die Leitline zu
				if abs(a.getLeitstrahlWinkel - self.getDirection) > 1:
					result = 0		
				"""
		#nahe der Soll? dann Lenkung in gegenrichtung, Dir wie solldir anstreben
		#mit sinkendem abstand schliesslich die leitstrahlrichtung .
		
		
		"""
		# bei 7331 abschaltung akku
		
import os

# Running a simple command
os.system("sudo shutdown -h now")
"""
		
		self.__lastStatic = b
		return result
				
		
		
		
def testPositionStatic():		
	print('\n----TEST START---------------------------------------------------------------')
	a = Position(3.31,-31,1)		
	b = Position(-0.24,-41,1)		

	r = Position(3.30,-31,1)		
	rs = RoverStatic(a,b,r)
	print('abstand ', rs.getAbstand())
	print('restWeg ', rs.getRestweg())
	print('--')
	r = Position(3.32,-31,1)		
	rs = RoverStatic(a,b,r)
	print('abstand ', rs.getAbstand())
	print('restWeg ', rs.getRestweg())

	
	print('---------END-----------------------------------------------------------------')
	
#test()	
	
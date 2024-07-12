import math
#import basisstation

class Position:
	"""Koordinatenpaar lon lat """
	def __init__(self, lat, lon):	
	  self.x=lat
	  self.y=lon
	  print('a: ' + str(self.x) + ', ' + str(self.y))
	  
print('test.py\n\n')

class RoverStatic:
	"""akt. statische Situation des Rover zur akt. StartZielLinie """
	def __init__(self,start, ziel, rover):
		self.__a = start
		self.__b = ziel
		self.__r = rover
		self.__dirLeitstrahl = 0.0
		self.__dirZielstrahl = 0.0
		self.__delta = 0.0
		self.__rest = 0.0 
		self.calc()
	
	def getDirLeitstrahl(self):			
		return self.__dirLeitstrahl		
	def getDirZielpunkt(self):		
		return self.__dirZielstrahl		
	def getDelta(self):
		return self.__delta
	def getRest(self):
		return self.__rest		
	def getRoverPosition(self):
		return self.__r
	

		
	def calc(self):
		print("calc----------------------------")
		wsoll = (self.__b.y - self.__a.y)/(self.__b.x - self.__a.x)
		wsoll = math.atan(wsoll)
		print('wsoll:',wsoll,' ', math.degrees(wsoll))
		wsoll = math.atan2(self.__b.y - self.__a.y, self.__b.x - self.__a.x)	
		print('wsoll:',wsoll,' ', math.degrees(wsoll))
		self.__dirLeitstrahl = wsoll

		wrover = (self.__b.y - self.__r.y)/(self.__b.x - self.__r.x)
		wrover = math.atan(wrover)
		print('wrover',wrover,' ', math.degrees(wrover))
		wrover = math.atan2(self.__b.y - self.__r.y, self.__b.x - self.__r.x)
		print('wrover',wrover,' ', math.degrees(wrover))
		self.__dirZielstrahl = wrover

		# Wenn wrover > wsoll muss nach links gelenkt werden.
		# der Abstand von der Sollinie
		#pythagoras
		h = math.pow(self.__b.y - self.__r.y , 2) + math.pow(self.__b.x - self.__r.x , 2)
		h = math.pow(h, 0.5)
		print('h '+ str(h))

		# Abstand sinus  positiv heisst rechts von soll. also nach links lenken
		self.__delta = h * math.sin(wrover - wsoll)
		print('delta '+ str(self.__delta))
		
		# Punkt Lot , ist er noch vor dem Ziel? positiv heisst vor dem ziel 
		self.__rest = h * math.cos(wrover - wsoll)
		print('rest '+ str(self.__rest))
		

a = Position(5.0,5.0)	  
b = Position(15.0,10.0)
c = Position(15.0,15.0)
d = Position(15.0,0.0)

r = Position(10,5)
r1 = Position(5.0,0.0)
r2 = Position(0.0,11.0)
r3 = Position(16.0,12.0)
r4 = Position(16.0,9.0)
r5 = Position(15.5,9.0)

		
"""
x = RoverStatic(a,b,r)
x.calc()
x = RoverStatic(a,c,r)
x.calc()
x = RoverStatic(a,d,r)
x.calc()

x = RoverStatic(a,b,r)
#x.calc()
x = RoverStatic(a,b,r1)
#x.calc()
x = RoverStatic(a,b,r2)
#x.calc()
x = RoverStatic(a,b,r3)
#x.calc()
x = RoverStatic(a,b,r4)
#x.calc()
x = RoverStatic(a,b,r5)
#x.calc()
print('r5delta: ',x.getDelta())
print('r5rest : ',x.getRest())
"""

'''
zyklisch lenkung nachstellen
wenn abstand sinkt dann in gegenrichtung  und umgekehrt
Also Abstand merken

stoppen am ende

richtung des rovers berechnen aus letzter pos und akt. pos, also merken mit zeitstempel und fix



'''


class RoverDynamic:
	""" dynamischer Zustand des Rovers
	Merken des letzen Abstandes um stärker zu lenken oder bereits gegen zu lenken
	Merken der letzten Position, um die Richtung zu bestimmen
	Takten der Aktualisierung
	"""
	def __init__(self):
		print('RoverDynamic init')
		self.__lastStatic = None	
		self.__lastDirection = None;
		self.__direction = None;
		
		
	def calcDirection(self, rStatic):
		a = self.__lastStatic.getRoverPosition()
		b = rStatic.getRoverPosition()		
		dir = math.atan2(b.y - a.y,b.x - a.x)
		print('dir:',dir,' ', math.degrees(dir))
		self.__direction = dir
		
				
	def action(self,rStatic):
		print('RoverDynamic action')		
		a = self.__lastStatic
		b = rStatic
		if a is None:
			self.__lastStatic = b
			return
		self.calcDirection(b)
		
		# Abstand welche Seite? Links oder rechts lenken	
		
		# Abstand wird nicht kleiner? Dann stärker lenken, sonst gerade
			
		# Abstand wird kleiner: Richtung parallel zum Leitstrahl gegenlenken
		
		# nahe der Soll? dann Lenkung in gegenrichtung, Dir wie solldir anstreben
		
		# überfahren der linie gegenrichtung lenken (wird nicht kleiner)
				
		# am Ende auch die letzte Richtung merken
		self.__lastDirection = self.__direction
		self.__lastStatic = b
		
		
r = Position(10,5)	
r1 = Position(5.0,0.5)	


		
rd = RoverDynamic()

rs1 = RoverStatic(a,b,r1)
rs1.getRichtungLeitlinie()
rd.action(rs1)
# ...
rs2 = RoverStatic(a,b,r)
rd.action(rs2)
# ... usw.
		
		
		
		
		
	
	
		
		

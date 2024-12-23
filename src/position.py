import math
import mqtt_test
import json  
import time
import roverparams
import offset

nahAbstand = 0.06 
iAbstand = 65



def saveiAbstand(ab):
	global iAbstand
	iAbstand = ab
def getiAbstand	():
	global iAbstand
	return iAbstand


class Position:
	"""Koordinatenpaar lon lat mit fix"""
	def __init__(self, lon, lat, fix):	
		self.x=lon
		self.y=lat
		self.fix=fix
		#print('a: ' + str(self.x) + ', ' + str(self.y)+ ', ' + str(self.fix))
	def round(self):
		self.x=round(self.x,2);
		self.y=round(self.y,2);
	def __str__(self):
		return '[x:'+str(self.x) + ", y:" + str(self.y)+']'
	def copy(self):
		result = Position(self.x,self.y,self.fix)
		return result
	  
class RoverStatic:
	"""akt. statische Situation des Rover zur akt. StartZielLinie """
	def __init__(self, start, ziel, rover):
		self.__a = start
		self.__b = ziel
		self.__r = rover
		self.__leitstrahlwinkel = 0
		self.__roverzielwinkel = 0
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
		
	 
	def getPositJson(self):
		return json.dumps({"leitwinkel": round(math.degrees(self.__leitstrahlwinkel),1),"abstand": round(self.__delta,2),"rest": round(self.__rest,2)})
		
	def calc(self):
		#print("calc----------------------------")
		#wsoll = math.atan2(self.__b.y - self.__a.y, self.__b.x - self.__a.x)
		wsoll = math.atan2(self.__b.x - self.__a.x, self.__b.y - self.__a.y)
		if(wsoll < 0):
			wsoll = 2 * math.pi + wsoll
		self.__leitstrahlwinkel = wsoll			
		#mqtt_test.mqttsend('leitwinkel', round(math.degrees(wsoll),1))	
		
		wrover = math.atan2(self.__b.x - self.__r.x, self.__b.y - self.__r.y)
		self.__roverzielwinkel = wrover
		#print('wrover',wrover,' ', round(math.degrees(wrover),2),' Grad')

		# Wenn wrover > wsoll muss nach links gelenkt werden.
		# der Abstand von der Sollinie
		#pythagoras
		h = math.pow(self.__b.y - self.__r.y , 2) + math.pow(self.__b.x - self.__r.x , 2)
		h = math.pow(h, 0.5)
		#print('h '+ str(h))

		# Abstand sinus  positiv heisst rechts von soll. also nach links lenken
		self.__delta = round(h * math.sin(wsoll - wrover),2)
		#print('abstand '+ str(self.__delta))
		#mqtt_test.mqttsend('abstand',self.__delta)	
		
		# Punkt Lot , ist er noch vor dem Ziel? positiv heisst vor dem ziel 
		self.__rest = round(h * math.cos(wrover - wsoll),2)
		#print('rest '+ str(self.__rest))
		#mqtt_test.mqttsend('rest',self.__rest)	
		#print(self.__leitstrahlwinkel)
		mqtt_test.mqttsend('position',self.getPositJson())
	
	
		
class RoverDynamic:
	""" dynamischer Zustand des Rovers
	Merken des letzen Abstandes um stärker zu lenken oder bereits gegen zu lenken
	Merken der letzten Position, um die Richtung zu bestimmen
	Takten der Aktualisierung
	"""
	iAbstand = 0  #integraler Anteil der Regelung
	
	def __init__(self):		
		self.__lastStatic = None	
		#self.iAbstand = getiAbstand()
		self.params = roverparams.getParamFile()		
		#print('Rover Params', self.params)
		self.iAbstand = offset.readOffset() #self.params['iWert']		
		self.iAbstand = 0 
		#print('init iAbstand',self.iAbstand)		
		mqtt_test.mqttsend('params', json.dumps(self.params, indent=4))
				
	def getDirection(self, rStatic):
		dir = 0
		if not (self.__lastStatic is None):
			a = self.__lastStatic.getRoverPosition()
			b = rStatic.getRoverPosition()		
			dir = math.atan2(b.y - a.y, b.x - a.x)
		#print('dir:',dir,' ', math.degrees(dir))
		return dir
		
	def getWeg(self, rStatic):
		s = 0
		if not (self.__lastStatic is None):
			r = self.__lastStatic.getRoverPosition()
			b = rStatic.getRoverPosition()		
			#pythagoras
			s = math.pow(b.y - r.y , 2) + math.pow(b.x - r.x , 2)
			s = math.pow(s, 0.5)
			s = round(s,2) # 0.05
			print('position.getWeg:',s)
		return s
		
	def getRoverPosJson(self, abstand, deltadir):
		return json.dumps({"abstand": round(abstand,2),"winkel": round(math.degrees(deltadir),1)})				
		
	def getRoverSollvorgabe(self,leit,p,i,gesamt):
		return json.dumps({"leit": leit,"P": p,"I": i,"gesamt": gesamt})
				
	def getLenkrichtungDynamisch(self,rStatic):
		'''				
		Sollwinkel für bearing ist erstmal leitwinkel
		Wenn Abstand dann Gegenlenken, also Sollwinkel in die Richtung ändern:
		P Je größer der Abstand desto größer der Offset.
		I einen festen Anteil langsam ändern und immer mitführen
		'''
		a = self.__lastStatic
		b = rStatic			
		result = 0
		try:
			leit = b.getLeitstrahlWinkel()
			leit = round(math.degrees(leit),1)
			abstand = b.getAbstand() #links minus, rechts plus			
			#meter nach winkel. je weiter weg umso stärker hinlenken
			#print('abstand',abstand)
			pAbstandwinkel = abstand * 30 #10 #60 #20  # 100 ==> 1 cm 1 grad
			'''
			pAbstandwinkel = abstand * self.params['pWert']
			pAbstandwinkel = max(-self.params['pMax'],pAbstandwinkel)
			pAbstandwinkel = min(self.params['pMax'],pAbstandwinkel)			
			pAbstandwinkel = round(pAbstandwinkel,1)
			'''
			#meter in einen Anteil wandeln, der zu einem I-Anteil addiert wird.
			#10 cm = 0.10 m = 1 Grad			
			weg = self.getWeg(b)
			if weg >= 0.05:  #ein merklicher weg zurückgelegt. Nicht festgefahren
				if abstand < 0.1: # nur Feinjustierung
					i = abstand * self.params['iFaktor'] # meter in gradschritte
					#i=0
					self.iAbstand += -i
					self.iAbstand = round(self.iAbstand,5)
			self.iAbstand=0
			#
			#self.iAbstand = max(-self.params['iMax'],self.iAbstand)
			#self.iAbstand = min(self.params['iMax'],self.iAbstand)
			#self.iAbstand = round(self.iAbstand,2)
			#saveiAbstand(self.iAbstand)
			#
			#leit wird korrigiert, um abstand zu verringern und 
			# offset zwischen gps-Richtung und compass-Richtung auszugleichen
			
			#print(pAbstandwinkel)
			pAbstandwinkel = min(pAbstandwinkel,90)
			#print(pAbstandwinkel)
			pAbstandwinkel = max(pAbstandwinkel,-90)
			print('leitwinkel:',leit,'abstandswinkel:',pAbstandwinkel)			
			result = leit - pAbstandwinkel + self.iAbstand  #abstand links muss winkel vergrößern			
			#result = -result
			while result > 360:
				result -= 360
			while result < 0:
				result += 360
			result = round(result,1)
			mqtt_test.mqttsend('sollvorgabe',self.getRoverSollvorgabe(leit,pAbstandwinkel,self.iAbstand,result))
			offset.writeOffset(self.iAbstand) # nur schreiben weil nächstes Object beim Wenden generiert wird
			print('Abstand:',abstand,'offset:',self.iAbstand)
		except  Exception as e:
			print('error '+repr(e))
		finally:			
			self.__lastStatic = rStatic
			return result
			
		
	
	
				
	def getLenkrichtungDynamischNurGPS(self,rStatic):
		""" 
		das weitergegenlenken wird bei Abstandsverringerung abgebrochen 
		"""	
		
		a = self.__lastStatic
		b = rStatic				
		try:
			result = 0	
			if (a is not None):				
				rdir = self.getDirection(b)				
				leit = b.getLeitstrahlWinkel()					
				mqtt_test.mqttsend('lenkpos', self.getRoverPosJson(b.getAbstand(),leit-rdir))
				#
				result = b.getLenkrichtung() 					
				if (b.getAbstand() < 0) == (a.getAbstand() < 0):
					# normalfall: auf einer Seite des Leitstrahls
					if abs(b.getAbstand()) < abs(a.getAbstand()):
						result = 0
						# jetzt Dynamics: Wenn Nahe der Leitlinie, schon vorher gegenlenken 						
						print(b.getAbstand())
						if abs(b.getAbstand()) < nahAbstand:
							rdir = self.getDirection(b)				
							leit = b.getLeitstrahlWinkel()
							#print('leit: ', round(math.degrees(leit),2), ', rover:', round(math.degrees(rdir),2) )
							if abs(rdir-leit) > math.radians(10):
								# jetzt gegenlenken
								match b.getLenkrichtung():
									case 1:  result = -1
									case -1: result = 1
														
						
					
		finally:			
			self.__lastStatic = rStatic
			return result
				
				
		"""
				# oder weiter gegenlenken, aber nicht steiler als  45 grad auf die Leitline zu
				if abs(a.getLeitstrahlWinkel - self.getDirection) > 1:
					result = 0		
		
				
		#nahe der Soll? dann Lenkung in gegenrichtung, Dir wie solldir anstreben
		#mit sinkendem abstand schliesslich die leitstrahlrichtung .
		
				#if abs(b.getAbstand()) < 0.6:  # nah gehe auf winkel Leitstrahl
					
				
		
		
		"""
		

"""		
import os

# Running a simple command
os.system("sudo shutdown -h now")
"""
				
		
		
		
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
	
	
	
def testPositionDynamic():
	global nahAbstand 
	nahAbstand = 0.6 #für den testfall
	
	a = Position(10.0,0.0,1)		
	b = Position(10.0,10.0,1)		
	rd = RoverDynamic()

	rpos = [
		Position(9.9, 0.0, 1),
		Position(9.0, 1.5 ,1),	
		Position(8.5, 3.5, 1),		
		Position(9.0, 6.0, 1),	
		Position(9.5, 6.5, 1),				
		Position(10.5, 8.0, 1)		
	]
	
	i=0
	for pos in rpos:
		i += 1 
		rs = RoverStatic(a,b,pos)
		leit = rs.getLeitstrahlWinkel()
		rdir = rd.getDirection(rs)								
		v = rd.getLenkrichtungDynamisch(rs)
		#print('leit: ', round(math.degrees(leit),2), ', rover:', round(math.degrees(rdir),2) )
		print(rd.getRoverPosJson(rs.getAbstand(), leit-rdir))
		print (i,pos.x, pos.y,'lenkStat: ',rs.getLenkrichtung() ,'lenkDyn:', v)
		#if i==5:			break
		time.sleep(0.2)
	
	
	
def testLenk():
	offset.writeOffset(0.1)
	a = Position(0.0,0.0,1)		
	#
	b = Position(10.0,10.0,1)
	c = Position(0.0,10.0,1)
	d = Position(-10.0,10.0,1)
	e = Position(-10.0,0.0,1)
	f = Position(-10.0,-10.0,1)
	g = Position(0.0,-10.0,1)
	h = Position(10.0,-10.0,1)
	i = Position(10.0,0.0,1)
	bb = [b,c,d,e,f,g,h,i]
	#bb=[]
	#bb.append(c)
	#bb.append(b)
	
	r = Position(1.0,1.0,1)
	time.sleep(2)
	
	print('\n\n\n')
	for j in bb:		
		rd = RoverDynamic()
		rs = RoverStatic(a,j,r)
		leit = rs.getLeitstrahlWinkel()
		leit = round(math.degrees(leit),1)
		alpha = rd.getLenkrichtungDynamisch(rs)					
		print(j,'rover',r,'leit',leit,'alpha',alpha)
		
	print('\n\n\n')
	r = Position(-1.0,-1.0,1)
	for j in bb:		
		rd = RoverDynamic()
		rs = RoverStatic(a,j,r)
		leit = rs.getLeitstrahlWinkel()
		leit = round(math.degrees(leit),1)
		alpha = rd.getLenkrichtungDynamisch(rs)					
		print(j,'rover',r,'leit',leit,'alpha',alpha)
		
		

def testWeg():
	offset.writeOffset(0.0)
	a = Position(0.0,0.0,1)		
	b = Position(10.0,10.0,1)
	r = Position(1.0,1.0,1)
	w = Position(2.0,2.0,1)
	rd = RoverDynamic()
	time.sleep(1)
	print('--------------------------------')
	rs = RoverStatic(a,b,r)
	alpha = rd.getLenkrichtungDynamisch(rs)	
	print('alpha',alpha)
	rs = RoverStatic(a,b,w)
	alpha = rd.getLenkrichtungDynamisch(rs)	
	print('alpha',alpha)
	

if __name__ == "__main__":
	#test()	
	#testPositionDynamic()
	testLenk()
	#testWeg()
	

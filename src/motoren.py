import time
import RPi.GPIO as GPIO          
from time import sleep
from mqtt_test import mqttsend 
import math
import json


oa1 = 24
oa2 = 23
ena = 25

ob1 = 27
ob2 = 17
enb = 22
 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(oa1,GPIO.OUT)
GPIO.setup(oa2,GPIO.OUT)
GPIO.setup(ena,GPIO.OUT)
GPIO.output(oa1,GPIO.LOW)
GPIO.output(oa2,GPIO.LOW)
pa=GPIO.PWM(ena,1000)
pa.start(60)

GPIO.setup(ob1,GPIO.OUT)
GPIO.setup(ob2,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)
GPIO.output(ob1,GPIO.LOW)
GPIO.output(ob2,GPIO.LOW)
pb=GPIO.PWM(enb,1000)
pb.start(99)

power = 99
motorstop = True
forward = True

def setPower(p):
	global power
	power = p
	#pa.ChangeDutyCycle(p)  
	#pb.ChangeDutyCycle(p)  	
def setBackward():
	GPIO.output(oa1,GPIO.HIGH)
	GPIO.output(oa2,GPIO.LOW)  
	GPIO.output(ob1,GPIO.HIGH)
	GPIO.output(ob2,GPIO.LOW)  
def setForward():		
	GPIO.output(oa1,GPIO.LOW)
	GPIO.output(oa2,GPIO.HIGH)  
	GPIO.output(ob1,GPIO.LOW)
	GPIO.output(ob2,GPIO.HIGH)  
def stop():
	global motorstop
	motorstop = True
	GPIO.output(oa1,GPIO.LOW)
	GPIO.output(oa2,GPIO.LOW)
	GPIO.output(ob1,GPIO.LOW)
	GPIO.output(ob2,GPIO.LOW)
	pa.ChangeDutyCycle(0)  
	pb.ChangeDutyCycle(0)  
	#mqttsend('direction','stop')	
def start():
	global motorstop
	motorstop = False

def getMotorenJson(links,rechts):
		return json.dumps({"links": round(links,1),"rechts": round(rechts,1)})
def lenke(o,fahrtrichtung):	
	global motorstop
	if not motorstop:
		r = power + o
		r = min(100.0,r)
		r = max(-100,r)		
		'''
		vorwärts und r > 0
		nicht vorwärts und nicht r > 0
		'''
		if (r>=0)^(not fahrtrichtung):
			GPIO.output(oa1,GPIO.LOW)
			GPIO.output(oa2,GPIO.HIGH)  
		else:
			GPIO.output(oa1,GPIO.HIGH)
			GPIO.output(oa2,GPIO.LOW)  
		if r < 0:
			r = -r
		r = round(r,1)
		l = power - o 
		l = min(100.0,l)
		l = max(-100.0,l)
		if (l>=0)^(not fahrtrichtung):
			GPIO.output(ob1,GPIO.LOW)
			GPIO.output(ob2,GPIO.HIGH)
		else:
			GPIO.output(ob1,GPIO.HIGH)
			GPIO.output(ob2,GPIO.LOW)
		if l < 0:
			l = -l
		l = round(l,1)
		if fahrtrichtung:
			L = l
			R = r
			pa.ChangeDutyCycle(r)  
			pb.ChangeDutyCycle(l)
		else:
			L = r
			R = l
			pa.ChangeDutyCycle(l)  
			pb.ChangeDutyCycle(r)
		mqttsend('motors', getMotorenJson(L,R))	
	else:
		mqttsend('motors', getMotorenJson(0,0))	
	
def gerade():
	pa.ChangeDutyCycle(power)  
	pb.ChangeDutyCycle(power)  
def rechts():
	pa.ChangeDutyCycle(power)  
	pb.ChangeDutyCycle(power -30)  
def links():	
	pa.ChangeDutyCycle(power -30)  
	pb.ChangeDutyCycle(power)  
def setRichtung(i):	
	if i==0:
		gerade()
		mqttsend('direction','gerade')	
	elif i==1:
		rechts()
		mqttsend('direction','rechts')	
	elif i==-1:
		links()
		mqttsend('direction','links')	
	else:
		gerade()
		mqttsend('direction','gerade')	


def playRichtungen():
	setRichtung(1)
	sleep(1)
	setRichtung(-1)
	sleep(1)
	setRichtung(0)
	sleep(1)
	setRichtung(2)
	sleep(1)	
		
def play():	
	setPower(50)
	setBackward()
	sleep(1)
	setForward()
	sleep(1)
	rechts()
	sleep(1)
	links()
	sleep(1)
	gerade()
	sleep(1)
	stop()
	
def stoptest():
	stop()
	setForward()
	setPower(80)
	lenke(0)
	time.sleep(2)
	print('start')
	start()
	lenke(0)
	time.sleep(2)	
	print('start')
	stop()
	lenke(0)
	while True:
		time.sleep(0.1)	
	
#stoptest()
#setRichtung(2)	
#play()	
#playRichtungen()
  
"""
  fahre 
  vor rück    schnell langsam
  rechts links  schwach stark sehr stark
  selbstlernend je nach untergrund
  
  startpunkt 
  zur linie
  entlang der linie
  abweichung von linie im vergleich mit vorher
  richtung wie leitline
  abweichung minimieren  
  takten sekundentakt
  
  zielrichtung
  letzte mit akt position bring akt. richtung
  drehen in zielrichtung über kleinsten winkel, damit klar links oder rechts
  aber schnell eintauchen
  also maximal senkrecht auf leitline steuern als tendenz
  Abstand groß  ziel die leitline
  sonst ziel die zielpos
  
  erste lösung: 
  links rechts berechnen anhand Ist/Ziel-Richtung und 
  P-Anteil Abstand in cm   und daraus eine SollZielrichtung und diese regeln P
  I-Anteil mittlere Abweichung (Hang)   
  D-Anteil ACC Modul
  
  
  
  
  letzte messung
  akt
  fahrtrichung winkel
  zielpunkt  winkel
  daraus links rechts
  
  abstand zur solllinie (Start + Zielpunkt)
  
  erster versuch 
  startpunkt und zielpunkt ist fest programmiert
  setzen des Fahrzeuges, starten in irgendeine richtung
  es muss anfahren, in die korrekte richtung drehen und der linie folgen.
  
  Am Ziel werden Start und Ziel getauscht für den Dauertest.
  
  Optimieren des Reglers im Betrieb per KI
  
  
  
  
  
  
  
  
  
  
"""
  
  
  
  
  
  


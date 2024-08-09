import time
import RPi.GPIO as GPIO          
from time import sleep
from mqtt_test import mqttsend 
import math
import json


ob2 = 24
ob1 = 23
enb = 25

oa2 = 27
oa1 = 17
ena = 22
 
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
def getMotorenJson(ri,val,links,rechts,fl,fr):
		return json.dumps({"richtung":ri,"val":val, "links": round(links,1),"rechts": round(rechts,1),"FL":fl,"FR":fr})
def lenke(o,fahrtrichtung):	 #o wert +rechts, -links, 0 mitte, rückwärts motoren wechseln und drehrichtung wechseln
	global motorstop
	if not motorstop:
	#rückwärts: rechts und links tauschen: zuerst die werte, dann die polung. 
		if not fahrtrichtung: #in Gegenrichtung lenken
			o = -o
	    
		r = power + o
		r = min(100.0,r)
		r = max(-100,r)
		r = round(r,1)
		
		l = power - o 
		l = min(100.0,l)
		l = max(-100.0,l)
		l = round(l,1)
		
		  
		'''
		vorwärts und r > 0
		nicht vorwärts und nicht r > 0
		'''
		fr = 0 #Drehrichtung umdrehen
		if (r>=0)^(not fahrtrichtung):
			fr=1
			GPIO.output(oa1,GPIO.LOW)
			GPIO.output(oa2,GPIO.HIGH)  
		else:
			fr=-1
			GPIO.output(oa1,GPIO.HIGH)
			GPIO.output(oa2,GPIO.LOW)  
		if r < 0:
			r = -r
		
	
		fl=0
		if (l>=0)^(not fahrtrichtung):
			fl=1
			GPIO.output(ob1,GPIO.LOW)
			GPIO.output(ob2,GPIO.HIGH)
		else:
			fl=-1
			GPIO.output(ob1,GPIO.HIGH)
			GPIO.output(ob2,GPIO.LOW)
		if l < 0:
			l = -l
		
		
		pa.ChangeDutyCycle(r)  
		pb.ChangeDutyCycle(l)
		L = l*fl
		R = r*fr
		mqttsend('motors', getMotorenJson(fahrtrichtung,o,L,R,fl,fr))	
	else:
		mqttsend('motors', getMotorenJson(True,0,0,0,0,0))	
	
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

def lenktest():
	t=5
	while True:
		stop()
		setPower(70)
		start()
		lenke(0,True)
		time.sleep(t)	
		lenke(30,True)
		time.sleep(t)	
		lenke(0,True)
		time.sleep(t)	
		lenke(-30,True)
		time.sleep(t)	
		stop()
		time.sleep(t)	
		time.sleep(t)	

	
    
		
		
#stoptest()

#lenktest()
#setRichtung(2)	
#play()	
#playRichtungen()
  
"""
  
"""
  
  
  
  
  
  


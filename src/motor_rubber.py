import time
import RPi.GPIO as GPIO          
from time import sleep

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
pa.start(50)

GPIO.setup(ob1,GPIO.OUT)
GPIO.setup(ob2,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)
GPIO.output(ob1,GPIO.LOW)
GPIO.output(ob2,GPIO.LOW)
pb=GPIO.PWM(enb,1000)
pb.start(50)




print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run s-stop f-forward b-backward l-low m-medium h-high e-exit")
print("\n")    
time.sleep(1) # Sleep for 3 seconds
while(1):
  #----------------------------------------------MOTOR A-----------------
  print("\nstart")
  GPIO.output(oa1,GPIO.HIGH)
  GPIO.output(oa2,GPIO.LOW)  
  GPIO.output(ob1,GPIO.HIGH)
  GPIO.output(ob2,GPIO.LOW)  
  time.sleep(1)
  print("faster")
  pa.ChangeDutyCycle(100)  
  pb.ChangeDutyCycle(100)  
  time.sleep(1) # Sleep for 3 seconds
  pa.ChangeDutyCycle(1)
  time.sleep(1) # Sleep for 3 seconds
  pa.ChangeDutyCycle(100) 
  time.sleep(1) # Sleep for 3 seconds
  pb.ChangeDutyCycle(1)
  time.sleep(1) # Sleep for 3 seconds
  pb.ChangeDutyCycle(100) 
  time.sleep(3) # Sleep for 3 seconds

  print("stop R")
  GPIO.output(oa1,GPIO.LOW)
  GPIO.output(oa2,GPIO.LOW)
  GPIO.output(ob1,GPIO.LOW)
  GPIO.output(ob2,GPIO.LOW)
    
  time.sleep(5) # Sleep for 3 seconds
  
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
  
  
  
  
  
  


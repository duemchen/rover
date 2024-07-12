from position import Position,RoverStatic,RoverDynamic
import compass_i2c
bus = None

i2c_address = 0x62


a = Position(3.31,-31.5,1)	  
b = Position(-0.24,-41.33,1)
r = Position(3.31,-31.5,1)	  #startpos
rs = RoverStatic(a,b,r)
soll = rs.getLeitstrahlWinkel()
soll = round(math.degrees(soll),1)) 

while True    
	ist = compass_i2c.bearing16()
	#mqtt_test.mqttsend('istwinkel', round(compass_i2c.bearing16(),1))
	mqtt_test.mqttsend('istwinkel', ist)
	delta = ist - soll
	mqtt_test.mqttsend('deltawinkel', delta)
	
	


#test()


'''
Lenkung sorgt für die Einhaltung einer Sollrichtung (Himmelsrichtung)
Sollwinkel einhalten, also sehr gerade fahren und sofort reagieren
P Abstand. Lenkungswert nicht fest sondern proportional bis 0 oder negativ
I Langzeit	Mittelwert	addieren constante
D Änderung	Wenn plötzlich die Wirkung der Lenkung einsetzt/nachlässt, 
  diesem Ruck entgegenwirken.


Streckenabfahrt durch (langsame) Anpassung der Sollrichtung auf Basis GPS
Sollrichtung = Leitstrahlrichtung 
Abstand messen, wenn größer/kleiner wird dann anpassen. 
Parallelfahrt anstreben und dem Leitsrahl nähern
P  SollrichtungsDelta setzen: Abstand langsam verkleinern. Proportional
I  Mittelwert Abstand bilden
(D  entfällt. Schnelle Dinge werden oben getan.)


Wende
Umschaltung auf eine neue Sollrichtung 
- scharfe Reaktion wegen sehr großer Sollabweichung (Ketten laufen gegensinnig)
- in Sollrichtung drehen sofort
- neue Sollrichtung erstmals erreicht/geschnitten?
- dann Abstand ausregeln

'''

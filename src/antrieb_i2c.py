# raspi-config i2c aktivieren
# apt-get install i2c-tools
# i2cdetect -y 1  (0,2)
# sudo apt-get install python-smbus 
# pip install smbus # 2 --break-system-packages

# M32 Motortrieber Doppel-H-Brücke
# https://www.robot-electronics.co.uk/htm/md25i2c.htm#command%20register

import smbus
import time
import sys
import mqtt_test

bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
i2c_address = 0x58
batteryReg = 10
modeReg = 15
mode = 3 # beide motoren geschwindigkeit M1, turn M2
speedReg = 0
turnReg = 1

speed = 80
slowSpeed = speed
slowEnd = time.time() - 1 # bis dahin langsam fahren

def setSlow(sekunden,speed):
	global slowEnd,slowSpeed
	slowEnd = time.time() + sekunden
	slowSpeed = speed
	

class Antrieb:
	""" M25 2 Rad Antrieb """
	def __init__(self):	
		self.i2c_address = 0x58
		self.batteryReg = 10
		self.modeReg = 15		
		self.mode = 3 # beide motoren geschwindigkeit M1, turn M2
		self.speedReg = 0
		self.turnReg = 1	
		self.cmdReg = 16
		#
		self.bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
		self.bus.write_byte_data(i2c_address, modeReg, mode)
		self.motorStopAutomatic(True)

	def motorStopAutomatic(self, active):
		if active:
			self.bus.write_byte_data(i2c_address, self.cmdReg, 51)			
		else: 
			self.bus.write_byte_data(i2c_address, self.cmdReg, 50)				
			
	def setSpeed(self, speed): # -128...0...127
		self.bus.write_byte_data(i2c_address, speedReg, int(speed))

	def setTurn(self, turn):  # -128...0...127
		self.bus.write_byte_data(i2c_address, turnReg, int(turn))
	
	def getVoltage(self):	
		result = self.bus.read_byte_data(i2c_address, self.batteryReg)
		result = round( result/10, 2)
		#print('Spannung: ', result)
		return str(result) #+' V'
			
	def lenke(self,turn,fahrtrichtung):
		global speed,slowSpeed,slowEnd		
		#speed absenken für einige sekunden
		if time.time() < slowEnd:
			spee = slowSpeed
		else: 
			spee = speed
		
		if fahrtrichtung:
			spee = spee
		else:
			spee = -spee
			turn = -turn
			
		turn = min(127,turn)
		turn = max(-128,turn)
		#print('turn',turn)
		spee = min(127,spee)
		spee = max(-128,spee)
		#print('spee',spee)
		self.setSpeed(spee)
		if spee == 0:
			self.setTurn(0) # im Stand nicht drehen. Sondern dann ausdrücklich mindestens speed 1 oder -1 
		else: 
			self.setTurn(turn)	# turn dreht selbst wenn spee negativ oder null ist.

# 
def testlauf():
	global speed
	speed = 50
	
	x=5
	'''
	fahre vorwärts in eine richtung
	fahre dann genau entgegengesetzt in die andere Richtung, also 180 grad andere richtung
	aber rückwärts. also bleibe so, drehe dich nicht um 180 grad!
	'''
	
	a = Antrieb()
	print(a.getVoltage())
	mqtt_test.mqttsend('voltage', a.getVoltage())
	a.motorStopAutomatic(not False)
	
	print('lenke vorwärts')
	a.lenke(-30,True)
	time.sleep(x)
	print('lenke rückwärts')
	a.lenke(-30,False)
	time.sleep(x)
	
	sys.exit()
	
	
	
	a.setTurn(0)	
	a.setSpeed(50)
	
	print('vorwärts')
	time.sleep(x)
	
	a.setTurn(-30)
	print('links')
	time.sleep(x)
	
	a.setTurn(+30)
	print('rechts')
	time.sleep(x)
	
	a.setTurn(0)
	print('gerade')
	time.sleep(x)
	
	a.setSpeed(-30)
	print('rückwärts')
	time.sleep(x)	
	
	a.setSpeed(0)
	print('stop')
	time.sleep(x)

if __name__ == "__main__":
	testlauf()
#a = Antrieb()
#print(a.getVoltage())
#a.motorStopAutomatic(True)

	

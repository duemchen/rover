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

speed = 100

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
		self.bus.write_byte_data(i2c_address, speedReg, speed)

	def setTurn(self, turn):  # -128...0...127
		self.bus.write_byte_data(i2c_address, turnReg, turn)
	
	def getVoltage(self):	
		result = self.bus.read_byte_data(i2c_address, self.batteryReg)
		result = round( result/10, 2)
		#print('Spannung: ', result)
		return str(result) #+' V'
			
	def lenke(self,turn,fahrtrichtung):
		global speed
		if fahrtrichtung:
			self.setSpeed(speed)
		else:
			self.setSpeed(-speed)
		self.setTurn(turn)	

# 
def testlauf():
	x=2
	
	a = Antrieb()
	print(a.getVoltage())
	mqtt_test.mqttsend('voltage', a.getVoltage())
	a.motorStopAutomatic(not False)
	
	print('lenke vorwärts')
	a.lenke(0,True)
	time.sleep(x)
	print('lenke rückwärts')
	a.lenke(0,False)
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

testlauf()
#a = Antrieb()
#print(a.getVoltage())
#a.motorStopAutomatic(True)

	

# raspi-config i2c aktivieren
# apt-get install i2c-tools
# i2cdetect -y 1  (0,2)
# sudo apt-get install python-smbus 
# pip install smbus # 2 --break-system-packages

import smbus
import time

bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
i2c_address = 0x60
bear8Reg = 0x01 #bearing
bear16Reg = 0x02 #bearing
calibReg = 0x1E 

def bearing8():
	b = bus.read_byte_data(i2c_address, bear8Reg)	
	b = round((360 * b / 255),1)
	return b
	
def bearing16():	
	b = bus.read_i2c_block_data(i2c_address, bear16Reg, 2)
	x = b[0] #*1.0
	y = b[1] #*1.0
	z = x*256 + y
	z =  z/10 
	return z
	
	
def readCalibration():
	b = bus.read_byte_data(i2c_address, calibReg)	
	print('readCalibration:', bin(b),'winkel: ', bearing16()) 
	
def storeCalibrationProfil():
	# 0xF0, 0xF5, 0xF6
	time.sleep(0.02)
	bus.write_byte_data(i2c_address, 0x00, 0xF0)
	time.sleep(0.02)
	bus.write_byte_data(i2c_address, 0x00, 0xF5)
	time.sleep(0.02)
	bus.write_byte_data(i2c_address, 0x00, 0xF6)
	time.sleep(0.02)

def delCalibrationProfil():
	# 0xE0, 0xE5, 0xE2
	time.sleep(0.02)
	bus.write_byte_data(i2c_address, 0x00, 0xE0)
	time.sleep(0.02)
	bus.write_byte_data(i2c_address, 0x00, 0xE5)
	time.sleep(0.02)
	bus.write_byte_data(i2c_address, 0x00, 0xE2)
	time.sleep(0.02)

def test():	
	while True:	
		print('bearing: ', bearing8(),' genau: ',bearing16())
		time.sleep(0.1)
		
def showcalib():
	while True:	
		readCalibration()	
		time.sleep(0.1)

#test()	
#storeCalibrationProfil()
#delCalibrationProfil()
#showcalib()
		
	
	

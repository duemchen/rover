# https://how2electronics.com/how-to-use-ads1115-16-bit-adc-module-with-raspberry-pi/


	
# sudo pip3 install adafruit-circuitpython-ads1x15 --break-system-packages
# sudo raspi-config nonint get_i2c   # 0 heisst ein
# sudo raspi-config nonint do_i2c 0  # so aktivieren 

import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
 
# Initialize the I2C interface
i2c = busio.I2C(board.SCL, board.SDA)
 
# Create an ADS1115 object
ads = ADS.ADS1115(i2c)
 
# Define the analog input channel
channel = AnalogIn(ads, ADS.P0)


def getVoltage():
	global channel 
	return channel.value
 
# Loop to read the analog input continuously

#while True:
#    print("Analog Value: ", channel.value, "Voltage: ", channel.voltage)
#    time.sleep(0.9)
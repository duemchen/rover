import threading
import time
import mqtt_test
import ADS1115_RaspiPython
import os
import json

#bei 8950 100% direkt nach laden und einschalten
#bei 7331 abschaltung akku

full = 8950
down = 7500



def stateJson():
	volt = ADS1115_RaspiPython.getVoltage()
	percent = 100* (volt - down) / (full - down)
	percent = int(percent)

	dictionary = {
		"voltage": volt,
		"percent": str(percent) +" %"
		
	}
	# Serializing json
	return json.dumps(dictionary, indent=4)


def server_status():
	"""Simulated function to print server status every 2 seconds."""
	while True:
		# This will print indefinitely until the main program exits
		# print("Voltage to mqtt")
		mqtt_test.mqttsend('voltage',stateJson())
		
		time.sleep(10)
		if ADS1115_RaspiPython.getVoltage() < 7500:
			mqtt_test.mqttsend('voltage', 'Battery low. Shutdown.')
			time.sleep(5)		
			os.system("sudo shutdown now -h")
	print("stop")	
	
	
def startVoltage():	
	# Initialize the thread with the server_status function as its target
	t = threading.Thread(target=server_status)

	# Setting the thread as a daemon means it will automatically exit when the main program does
	t.daemon = True

	# Start the server status thread
	t.start()

def run_server():
	startVoltage()
	"""Simulated function for server main loop."""
	while True:
		time.sleep(1)
	
	for x in range(5):
		# Simulate the server doing some work
		print(x,"[Server]: Processing data...")
		time.sleep(1)



	
if __name__ == '__main__':
	run_server()  # Run the main server function
	print("Server shutdown.")

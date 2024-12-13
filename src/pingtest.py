import subprocess
import os
import sys
#sys.path.append(os.getcwd())
print (os.getcwd())
#res = subprocess.call("ping 8.8.8.8 -c 1 | grep 'received' | awk -F',' '{ print $2}' | awk '{ print $1}'", shell=True)
#print('\n1:',res)

#res = subprocess.call(["ping", "8.8.8.8", "-c1", "-W2", "-q"])
#print('\n2:',res)

def pinge(ip):
	res = subprocess.call(["ping", ip, "-c1", "-W2", "-q"], stdout=open(os.devnull, 'w'))
	#print(ip,res)
	return res == 0

def pingband():
	for i in range(20,40):
		ip = "192.168.10."+str(i)		
		if pinge(ip):
			print(ip,pinge(ip))

def getmyip():
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	#print(s.getsockname()[0])
	result = s.getsockname()[0]
	s.close()			
	return result 
	
def amionline():
	ip = getmyip()
	return pinge(ip)

def restart():
	import os
	#os.system("sudo shutdown now -h")
	os.system("sudo reboot")

def netcontrol():
	from logtool import Logger
	log = Logger(name='ping_log', prefix='ping', log_dir='/home/pi/logs').get_logger()
	log.setLevel('INFO')
	if amionline():
		log.info('ping ok') 
	else:
		log.info('ping error. Restart.') 
		restart()
	
if __name__ == '__main__':
	#print (getmyip())
	#pingband()
	print('i am online?', amionline())
	netcontrol()

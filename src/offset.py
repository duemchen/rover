from configparser import ConfigParser
import os
import sys

home_dir = os.path.expanduser("~")
print(home_dir)



ini='offset.ini'
#print('file', __file__)
dirname = os.path.dirname(__file__)

#ini=dirname+'/'+ini
ini=home_dir +'/.rover/'+ini
print('offset ini:', ini)
#sys.exit()

def writeOffset(val):
	global ini
	Config = ConfigParser()
	Config.read(ini)
	Config.set('compass', 'offset', str(val))
	with open(ini, 'w') as configfile:
		Config.write(configfile)
		configfile.close
	
def readOffset():
	global ini
	Config = ConfigParser()
	Config.read(ini)
	return Config.getfloat('compass', 'offset')

def init():
	global ini
	path = os.path.dirname(os.path.abspath(ini))
	#print(path)
	if not os.path.exists(path):
		os.mkdir(path)	
	if not os.path.isfile(ini):
		Config = ConfigParser()
		Config.add_section('compass')
		Config.set('compass','offset','0')
		with open(ini, 'w') as configfile:
			Config.write(configfile)
			configfile.close
			
		
def test():	
	i=  readOffset()
	i= 10.6+i   
	print ('read: ',readOffset(),i)
	#print ('write: ',writeOffset(-100))
	#print ('read: ',readOffset())

init() #must be!
#test() #comment out

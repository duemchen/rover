
import json
import os.path

filename = 'rover_params.json'
 
def toParamFile(p,pmax,iw,iF,imax):
	# Data to be written
	dictionary = {
		"pWert": p,
		"pMax": pmax,
		"iWert": iw,
		"iFaktor": iF,
		"iMax": imax,      
	}
	# Serializing json
	json_object = json.dumps(dictionary, indent=4)
	
	# Writing to sample.json
	with open(filename, "w") as outfile:
		outfile.write(json_object)
	
def getParamFile():
	# Opening JSON file
	with open(filename, 'r') as openfile:
		# Reading from json file
		result = json.load(openfile)
		return result




def test():
#	toParamFile(1,2,3,4,5)
#	print(getParamFile())
	x=getParamFile()
	print(x['pWert'],x['pMax'],x['iWert'],x['iFaktor'],x['iMax'] )
	print(type(x))


print(os.path.abspath(filename))	
if not os.path.isfile(filename):
	toParamFile(60,50,1,5,10)

test()
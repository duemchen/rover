
import json
import os.path
from position import Position

filename = '/home/pi/.rover/mapposition.json'
map = None 

def toMap(r):
	global map, filename
	map.append([r.x,r.y])	
	json_object = json.dumps(map, indent=2)	
	with open(filename, "w") as outfile:
		outfile.write(json_object)
	
def readmap(filename):
	with open(filename, 'r') as openfile:
		# Reading from json file
		mappe = json.load(openfile)
		print(mappe)
		result = []
		for i in mappe:
			p=Position(0,0,1)
			p.x = i[0]
			p.y = i[1]
			result.append(p)
		return result

def saveAktSection(a,b):
	global map,filename
	map = []
	toMap(a)
	toMap(b)
	
def loadAktSection():
	global filename
	m = readmap(filename)
	if len(m) == 2:
		if (m[0]!=None) & (m[1]!=None):
			return m[0],m[1]
	return None,None
	
def posAktSection(list):
# die Stelle in der map finden (2 punkte gemerkt.)
	m,n = loadAktSection()
	i = 0
	while i < len(list)-1:
		if list[i].x == m.x:
			if list[i].y == m.y:
				if list[i+1].x == n.x:
					if list[i+1].y == n.y:
						return i  #die vorposition
		i+=1
	return -1


def setArePosWeiter(are):
	list = are.getPattern()
	i=posAktSection(list)
	print("setArePosWeiter:",i)
	i = i-1
	i = max(-1,i) #war -2 
	are.setPos(i)
	return i

	
def test():
	global map,filename
	list = []
	a = Position(1.11,2.22,1)		
	b = Position(33.33,-44.44,1)
	saveAktSection(a,b)
	x,y = loadAktSection()
	print(x.x)
	print(y.y)	
	list.append(Position(0.0,0.0,1))
	list.append(Position(10.0,10.0,1))
	list.append(a)
	list.append(b)
	list.append(Position(1.0,1.0,1))
	list.append(Position(2.0,2.0,1))
	i=posAktSection(list)
	print(i)
	
	

	
if __name__ == '__main__':
	test()
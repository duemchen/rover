from position import Position
import area

def test():
	pa = Position(3.31-1,-31.5,1)	  
	pb = Position(-0.24-1,-41.33,1)
	pc = Position(-0.24+1,-41.33,1)
	pd = Position(3.31+1,-31.5,1)	  


	#a = area(Position(0.0,0.0,1),Position(-4.0,10.0,1),Position(12.0,12.0,1),Position(10.0,-2.0,1))
	a = area(pa,pb,pc,pd)
	a.setFurchenbreite(0.5)
	#a.calcPatternGitter()
	a.calcPatternLang()
	#a.calcPatternBreit()
	p = a.getPattern()
	print('geojson\n\n',getGeoJson(p),'\n')
	#die letzte Position wird in datei gespeichert. Ohne reset machen wir da weiter. Mit reset beginnen wir am Anfang
	#a.resetPos() 
	#a.getPosProz()
	#gesamtstrecke, reststrecke prozent
	while True:
		m,n = a.getNextSection()
		if m==None or n==None:
			print('Ziel erreicht.')
			break
		print('{: >6}'.format(m.x),'{: >6}'.format(m.y),'->','{: >6}'.format(n.x),'{: >6}'.format(n.y))
		
		
		
		#if len(ab)<2:
		#	break		
		#print(ab[0].x,ab[0].y,ab[1].x,ab[1].y) #liefert 2 positionen, sie neue Strecke, die abgefahren werden soll
		
def test1():
	are = area.prepare()
	
	#a=None
	#b=None
	while True:
		a,b = are.getNextSection()
		if a==None or b==None:
			print('Ziel erreicht.')
			break	
		print('{: >6}'.format(a.x),'{: >6}'.format(a.y),'->','{: >6}'.format(b.x),'{: >6}'.format(b.y))

test1()

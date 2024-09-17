import time
start = time.time()

# Ausführen des Codeblocks, den wir messen wollen
print('Hallo Welt!',time.time())

# Endzeit bestimmen
end = time.time()

# Berechnung der verstrichenen Zeit
verstrichene_zeit = end - start
print(f'Ausführungszeit: {verstrichene_zeit} Sekunden')


slowtime = time.time() +5

while True: 
	if(time.time() < slowtime):
		print('slow')
		time.sleep(0.5)
		continue
	print('end!')
	break
		

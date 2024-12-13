import os
#os.system("sudo shutdown now -h")
#os.system(cat /proc/device-tree/model ; echo)



#result = os.system('cat /proc/device-tree/model; echo')

#print("mein Pi:", result, 'genau.')

import subprocess

command = 'cat /proc/device-tree/model;'
try:
    result = subprocess.check_output(command, shell=True, text=True)
    print('\nAA\n',result,'\nBB')
except subprocess.CalledProcessError as e:
    print(f('Error executing command: {e}'))
	
#sudo apt update && sudo apt full-upgrade && sudo apt autoremove

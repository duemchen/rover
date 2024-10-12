# SuperFastPython.com
# example of running the asyncio event loop in a separate thread
import threading
import asyncio
import time
import async_bearing
from datetime import datetime
# main coroutine for the asyncio program
# run other tasks for some time
async_bearing.startbearing()
for _ in range(10000000):
    # report a message
    print('>Main thread is running',datetime.now(),_)
    # sleep a moment
    time.sleep(0.5)
	
print('>Main thread END.')
from picamera import PiCamera
from time import sleep
import time
import sys
import subprocess
import os

camera = PiCamera(resolution=(1280,720))
#camera.iso= 800

dest = sys.argv[1]
recentPhotos = []

def convert(count, destbase):
    command = ["convert","-delay","10","-loop","0"
        ]+recentPhotos[-count:]+[
        os.path.join(dest,destbase)]

    print("Convert: %s"%(" ".join(command)))
    subprocess.call(command)
    

while True:
    start = time.time()
    destname = time.strftime("image-%Y-%m-%d-%H-%M-%S.jpeg")
    print("Taking %s"%destname)
    d = os.path.join(dest,destname)
    camera.capture(d)
    recentPhotos.append(d)

    convert(10,"Last10.gif")

    if len(recentPhotos) % 10 == 0:
        convert(100,"Last100.gif")

    if len(recentPhotos) % 100 == 0:
        convert(1000,"Last1000.gif")
        
    ## Tidy temp files
    
    ## Tidy timelapse files
    

    end = time.time()
    duration = end - start
    sleeptime = 120 - duration
    sleeptime = max(0,sleeptime)
    print("Sleeping for %d seconds"%sleeptime)
    time.sleep(sleeptime)
    

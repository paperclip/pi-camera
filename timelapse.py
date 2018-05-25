from picamera import PiCamera
from time import sleep
import time
import sys
import subprocess
import os

camera = PiCamera(resolution=(640,480))
#camera.iso= 800

dest = sys.argv[1]

photos = os.listdir(dest)
recentPhotos = [ os.path.join(dest,p) for p in photos if p.startswith("timelapse-") ]
recentPhotos.sort()

def convert(count, destbase):
    tempdest = os.path.join(dest,"temp.gif")
    finaldest = os.path.join(dest, destbase)
    command = ["convert","-delay","30","-loop","0"
        ]+recentPhotos[-count:]+[
        tempdest]

    print("Convert: %s %s"%(" ".join(command),destbase))
    subprocess.call(command)
    try:
        os.unlink(finaldest)
    except EnvironmentError:
        pass
    os.rename(
        tempdest,
        finaldest)

while True:
    start = time.time()
    destname = time.strftime("timelapse-%Y-%m-%d-%H-%M-%S.jpeg")
    print("Taking %s"%destname)
    d = os.path.join(dest,destname)
    camera.capture(d)
    recentPhotos.append(d)

    if len(recentPhotos) % 3 == 0:
        convert(10,"Last10.gif")

    if len(recentPhotos) % 20 == 0:
        convert(100,"Last100.gif")

    if len(recentPhotos) % 200 == 0:
        convert(1000,"Last1000.gif")
        
    ## Tidy temp files
    
    ## Tidy timelapse files
    

    end = time.time()
    duration = end - start
    sleeptime = 300 - duration
    sleeptime = max(0,sleeptime)
    print("Sleeping for %d seconds"%sleeptime)
    time.sleep(sleeptime)
    

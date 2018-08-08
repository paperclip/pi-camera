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
    command = ["nice","convert","-delay","30","-loop","0"
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

def cleanUpTimelapseFiles():
    global recentPhotos
    if len(recentPhotos) > 1500:
        print("Deleting 100 oldest photos")
        ## delete first 100 photos
        earlyPhotos = recentPhotos[:100]
        recentPhotos = recentPhotos[100:]
        for photo in earlyPhotos:
            try:
                os.unlink(photo)
                print("Deleted %s"%photo)
            except EnvironmentError:
                pass


def cleanUpTempFiles():
    pass

count = 0

while True:
    start = time.time()
    destname = time.strftime("timelapse-%Y-%m-%d-%H-%M-%S.jpeg")
    print("Taking %s"%destname)
    d = os.path.join(dest,destname)
    camera.capture(d)
    
    ## Throw away the picture if smaller than 50KiB - it'll be all black
    statbuf = os.stat(d)
    if statbuf.st_size < 50*1024:
		os.unlink(d)
		continue
    
    recentPhotos.append(d)

    if len(recentPhotos) % 3 == 0:
        convert(10,"Last10.gif")

    if len(recentPhotos) % 20 == 0:
        convert(100,"Last100.gif")

	## We won't every have MOD 200 == 0 since we bounce between 1501 -> 1401
    if count % 200 == 0:
        convert(500,"Last500.gif")

    ## Tidy temp files
    cleanUpTempFiles()

    ## Tidy timelapse files
    cleanUpTimelapseFiles()


    end = time.time()
    duration = end - start
    sleeptime = 300 - duration
    sleeptime = max(0,sleeptime)
    print("Sleeping for %d seconds"%sleeptime)
    time.sleep(sleeptime)
    count += 1


from picamera import PiCamera
from time import sleep
import time
import sys
import subprocess
import os
import datetime
import picamera

MAX_PHOTOS = 10000

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
    global MAX_PHOTOS
    if len(recentPhotos) > MAX_PHOTOS:
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
TIME_LAPSE_GIFS=False

def oneLoop(camera):
    global count
    global recentPhotos
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    destname = time.strftime("timelapse-%Y-%m-%d-%H-%M-%S.jpeg")
    print("Taking %s"%destname)
    d = os.path.join(dest,destname)
    camera.capture(d)
    
    ## Throw away the picture if smaller than 70KiB - it'll be all black
    statbuf = os.stat(d)
    if statbuf.st_size < 70*1024:
        print("Picture too small - night time")
        os.unlink(d)
    else:    
        recentPhotos.append(d)

        if TIME_LAPSE_GIFS:
            if len(recentPhotos) % 3 == 0:
                convert(10,"Last10.gif")

            if len(recentPhotos) % 20 == 0:
                convert(100,"Last100.gif")

            ## We won't every have MOD 200 == 0 since we bounce between 1501 -> 1401
            if count % 200 == 190:
                convert(500,"Last500.gif")
            else:
                print(count % 200)

        ## Tidy temp files
        cleanUpTempFiles()

        ## Tidy timelapse files
        cleanUpTimelapseFiles()
        
        count += 1

MAX_SLEEP_TIME = 120
    
def main():
    with picamera.PiCamera(resolution=(640,480)) as camera:
        #camera.iso= 800
        while True:
            start = time.time()
            oneLoop(camera)
            end = time.time()
            duration = end - start
            sleeptime = MAX_SLEEP_TIME - duration
            sleeptime = max(0,sleeptime)
            print("Sleeping for %d seconds"%sleeptime)
            time.sleep(sleeptime)
            
    return 0

sys.exit(main())

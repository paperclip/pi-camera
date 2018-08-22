from picamera import PiCamera
from time import sleep
import time
import sys
import subprocess
import os
import datetime
import picamera

dest = sys.argv[1]

def oneLoop(camera):
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    destname = time.strftime("timelapse-%Y-%m-%d-%H-%M-%S.jpeg")
    print("Taking %s"%destname)
    d = os.path.join(dest,destname)
    camera.capture(d)

MAX_SLEEP_TIME = 10.0
# RESOLUTION=(640,480)
RESOLUTION=(1920,1080)


def main():
    with picamera.PiCamera(resolution=RESOLUTION) as camera:
        #camera.iso= 800
        while True:
            start = time.time()
            oneLoop(camera)
            end = time.time()
            duration = end - start
            sleeptime = MAX_SLEEP_TIME - duration
            sleeptime = max(0,sleeptime)
            print("Sleeping for %f seconds"%sleeptime)
            time.sleep(sleeptime)

    return 0

sys.exit(main())

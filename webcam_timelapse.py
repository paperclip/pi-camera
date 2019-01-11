#!/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import cv2
import time
import os
import sys


def oneLoop(camera, dest):
    # camera.annotate_background = picamera.Color('black')
    # camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    destname = time.strftime("timelapse-%Y-%m-%d-%H-%M-%S.jpeg")
    print("Taking %s"%destname)
    d = os.path.join(dest,destname)
    return_value, image = camera.read()
    cv2.imwrite(d, image)

MAX_SLEEP_TIME = 45.0

def main(argv):
    dest = argv[1]
    camera = cv2.VideoCapture(0)
    try:
        #camera.iso= 800
        while True:
            start = time.time()
            oneLoop(camera, dest)
            end = time.time()
            duration = end - start
            sleeptime = MAX_SLEEP_TIME - duration
            sleeptime = max(0,sleeptime)
            print("Sleeping for %f seconds"%sleeptime)
            time.sleep(sleeptime)
    finally:
        del(camera)

    return 0

sys.exit(main(sys.argv))

from picamera import PiCamera
from time import sleep
import sys

camera = PiCamera(resolution=(1280,720))
#camera.iso= 800

# camera.start_preview()
#sleep(5)
dest = sys.argv[1]
camera.capture(dest)
# camera.stop_preview()

#!/usr/bin/python
# snagged and modded from https://cdn.hackaday.io/files/12450532660800/videoNoGPS.py

import picamera
import time
import numpy as np
import string
import random
import os
import socket
from ms5837 import ms5837

from PIL import Image, ImageDraw, ImageFont

# Video Resolution for recording
VIDEO_HEIGHT = 940
VIDEO_WIDTH = 1280

# directory where the video will be recorded
baseDir='/home/pi/osd/'

# Create empty images to store text overlays
textOverlayCanvas = Image.new("RGB", (704, 60))
textOverlayPixels = textOverlayCanvas.load()

# Use Roboto font (must be downloaded first)
font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf", 20)

# Make a 'zero' depth (default to -1 if not yet set)
zerodepth = -1

function getDepth():
	if zerodepth == -1:
		return "NOT YET ZEROED"
	
	return zerodepth - sensor.pressure() # TODO- check math

function getAngle():
	f = open("/var/cameraangle/cameraangle", "r")
	line = f.read(5)
	f.close()
	line = abs(line*90)
	return line

function getLateralDistance():
	if zerodepth == -1:
		return "NOT YET ZEROED"
	j = getAngle()
	d = getDepth()
	return ( sin(j)*(d) ) / (sin(90-j))

functin getMaxError():
	if zerodepth == -1:
		return "NOT YET ZEROED"
	y = getDepth()
	t = getAngle()
	
	return (d+4)*(tan(t+2)) - d*tan(t)

while sensor.read():
	data = conn.recv(1024)
	if data:
		data = str(data).rstrip('\n')
		print('PYTHON (depth-with-camera): received: ', data)
		if data == '0':
			zerodepth = sensor.pressure()

	with picamera.PiCamera() as camera:
	   camera.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)
	   camera.framerate = 60
	   camera.led = False
	   camera.start_preview()

	   topText = "Depth: "+getDepth()+" mm    Angle: "+getAngle()+" deg"
	   bottomText = "Lateral Distance to Target: "+getLateralDistance()+" meters (+/- "+getMaxError()+" cm)"

	   topOverlayImage = textOverlayCanvas.copy()
	   bottomOverlayImage = textOverlayCanvas.copy()

	   # Load the crosshair image
	   crosshairImg = Image.open('crosshair.png')

	   # Create an image padded to the required size with
	   crosshairPad = Image.new('RGB', (((crosshairImg.size[0] + 31) // 32) * 32, ((crosshairImg.size[1] + 15) // 16) * 16))
	   crosshairPad.paste(crosshairImg, (0, 0))

	   # Attach overlays 
	   topOverlay = camera.add_overlay(topOverlayImage.tostring(), size=(704,60), layer=3, alpha=128, fullscreen=False, window=(0,20,704,60))
	   bottomOverlay = camera.add_overlay(bottomOverlayImage.tostring(), size=(704,60), layer=4, alpha=128, fullscreen=False, window=(0,500,704,60))
	   crosshairOverlay = camera.add_overlay(crosshairPad.tostring(), size=(704,512), layer=5, alpha=10, fullscreen=False, window=(20,30,704,512))

	   try:
#		  while True:
			 topOverlayImage = textOverlayCanvas.copy()
			 bottomOverlayImage = textOverlayCanvas.copy()

			 drawTopOverlay = ImageDraw.Draw(topOverlayImage)
			 drawTopOverlay.text((200, 15), topText, font=font, fill=(255, 0, 255))

			 topOverlay.update(topOverlayImage.tostring())

			 drawBottomOverlay = ImageDraw.Draw(bottomOverlayImage)
			 drawBottomOverlay.text((150, 20), bottomText, font=font, fill=(255, 255, 255))

			 bottomOverlay.update(bottomOverlayImage.tostring())

#			 time.sleep(1)

#	   except KeyboardInterrupt:
#		  camera.remove_overlay(topOverlay)
#		  camera.remove_overlay(bottomOverlay)
#		  camera.remove_overlay(crosshairOverlay)
#
#		  print "Cancelled"
#
#	   finally:
#		  camera.remove_overlay(topOverlay)
#		  camera.remove_overlay(bottomOverlay)
#		  camera.remove_overlay(crosshairOverlay)

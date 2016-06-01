#!/usr/bin/pythonRoot

import sys, time, urlparse
from flup.server.fcgi import WSGIServer 

import RPi.GPIO as G   
G.setmode(G.BCM)

from RPIO import PWM 
s = PWM.Servo()

## Define pins for devices
## Step motor
pinStp = 20
pinDir = 21
pinSlp = 26

G.setup(pinStp, G.OUT)
G.setup(pinDir, G.OUT)

G.setup(pinSlp, G.OUT)
G.output(pinSlp, True)

## LED light
pinLED = 19

## Brushless motors
pinLft = 27
pinRgt = 22

s.set_servo(pinLft, 1000)
time.sleep(1.0)
s.set_servo(pinRgt, 1000)
time.sleep(0.5)

## Function for step motor
def stepMotor(step):
	G.output(pinSlp, False)
	time.sleep(0.1)
	# Direction
	if step < 0:
		G.output(pinDir, False)
	else
		G.output(pinDir, True)
	# step
	for i in range(1, step * 100):
		G.output(pinStp, True)
		G.output(pinStp, False)
		time.sleep(0.01)

	G.output(pinSlp, True)
	return
	

def app(environ, start_response):
	start_response("200 OK", [("Content-Type", "text/html")])
	i = urlparse.parse_qs(environ["QUERY_STRING"])
	yield ('&nbsp;') 
	#  url = "stp=-300&stp=50&lft=1050&rgt=1100&led=off"
	if "stp" in i:
		stepMotor(int(i["stp"][0]))
	if "lft" in i:
		s.set_servo(pinLft, int(i["lft"][0]))
	if "rgt" in i:
		s.set_servo(pinRgt, int(i["rgt"][0]))
	if "led" in i:
		if i["led"][0] == "on":
			G.setup(pinLED, G.OUT)
		else i["led"][0] == "on":
			G.cleanup(pinLED)

WSGIServer(app).run()

G.cleanup()


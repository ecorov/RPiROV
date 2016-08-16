#!/usr/bin/pythonRoot

import sys, time, urlparse
from flup.server.fcgi import WSGIServer 

import RPi.GPIO as G   
G.setmode(G.BCM)

from RPIO import PWM 
s = PWM.Servo(pulse_incr_us=1)

## Define pins for devices
## Step motor
pinStp = 21
pinDir = 20
pinSlp = 26

G.setup(pinStp, G.OUT)
G.setup(pinDir, G.OUT)
G.setup(pinSlp, G.OUT)
G.output(pinSlp, False)

## LED light
pinLED = 19

## Brushless motors
pinLft = 27
pinRgt = 22

pinDlyLft1 = 12
pinDlyLft2 = 13
pinDlyRgt1 = 5
pinDlyRgt2 = 6

s.set_servo(pinLft, 1000)
time.sleep(1.0)
s.set_servo(pinRgt, 1000)
time.sleep(0.5)

## Function for step motor
def stepMotor(step):
    G.output(pinSlp, True)
    time.sleep(0.1)
    # Direction
    if step < 0:
        G.output(pinDir, False)
    else:
        G.output(pinDir, True)
    # step
    for i in range(1, int(abs(step) * 1.8 *100)):
        G.output(pinStp, True)
        G.output(pinStp, False)
        time.sleep(0.0001)
    return
	

G.setup(pinLED, G.OUT)
time.sleep(1)
G.cleanup(pinLED)
G.setup(pinLED, G.OUT)
time.sleep(1)
G.cleanup(pinLED)


def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html")])
    i = urlparse.parse_qs(environ["QUERY_STRING"])
    yield ('&nbsp;') 
    #  url = "stp=-300&stp=50&lft=1050&rgt=1100&led=off"
    if "stp" in i:
        stepMotor(int(i["stp"][0]))
        G.output(pinSlp, False)
    if "lft" in i:
    	spd = int(i["lft"][0])
    	if spd < -1020:
    	    G.setup(pinDlyLft1, G.OUT)
    	    G.setup(pinDlyLft2, G.OUT)
    	    s.set_servo(pinLft, abs(spd))
    	else:
    	    G.cleanup(pinDlyLft1)
    	    G.cleanup(pinDlyLft2)
    	    s.set_servo(pinLft, abs(spd))
    if "rgt" in i:
    	spd = int(i["rgt"][0])
    	if spd < -1020:
    	    G.setup(pinDlyRgt1, G.OUT)
    	    G.setup(pinDlyRgt2, G.OUT)
    	    s.set_servo(pinRgt, abs(spd))
    	else:
    	    G.cleanup(pinDlyRgt1)
    	    G.cleanup(pinDlyRgt2)
    	    s.set_servo(pinRgt, abs(spd))
    if "led" in i:
        if i["led"][0] == "on":
            G.setup(pinLED, G.OUT)
        else:
            G.cleanup(pinLED)

WSGIServer(app).run()

G.cleanup()


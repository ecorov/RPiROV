#!/usr/bin/pythonRoot

import RPi.GPIO as G     
from flup.server.fcgi import WSGIServer 
import sys, urlparse


G.setmode(G.BCM)
G.setup(17, G.OUT)
G.setup(23, G.OUT)

def app(environ, start_response):
	start_response("200 OK", [("Content-Type", "text/html")])
	i = urlparse.parse_qs(environ["QUERY_STRING"])
	yield ('&nbsp;') 
	if "q" in i:
		if i["q"][0] == "w": 
			G.output(17, True)
			G.output(23, False)			
		elif i["q"][0] == "g": 
			G.output(23, True)	
			G.output(17, False)			
		elif i["q"][0] == "s":
			G.output(17, False)
			G.output(23, False)			


WSGIServer(app).run()



import sys, time, urlparse, RPIO
from flup.server.fcgi import WSGIServer

S = RPIO.PWM.Servo()

BM_lft = 27
BM_rgt = 17

SM_stp = 21
SM_slp = 21
SM_dir = 21

switch = 20


RPIO.setup(SM_stp, RPIO.OUT) # step motor: step
RPIO.setup(SM_slp, RPIO.OUT) # step motor: direction
RPIO.setup(SM_slp, RPIO.OUT) # step motor: sleep


time.sleep(1)
S.set_servo(BM_lft, 1000)
time.sleep(1)
S.set_servo(BM_rgt, 1000)
time.sleep(1)

def stepMotor(steps):
	RPIO.output(SM_slp, False)
	if steps < 0:
		RPIO.output(SM_dir, False)
	elif steps >=0:
		RPIO.output(SM_dir, True)
	
	for (i in step * 100):
		gpio.output(24, True)
		gpio.output(24, False)
		StepCounter += 1
		time.sleep(WaitTime)
	RPIO.output(SM_slp, True)	
	
def blMotor():

	
	
while StepCounter < steps:

    #turning the gpio on and off tells the easy driver to take one step
    gpio.output(24, True)
    gpio.output(24, False)
    StepCounter += 1

    #Wait before taking the next step...this controls rotation speed
    
	
	



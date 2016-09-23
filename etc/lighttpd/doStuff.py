#!/usr/bin/pythonRoot

import sys, time, urlparse, smbus, math, threading,struct

from shutil import copyfile

from flup.server.fcgi import WSGIServer 

from MS5803 import MS5803
from hmc5883l import hmc5883l

def readHMC5883L():
    thread = threading.currentThread() 
    hmc = hmc5883l(gauss = 4.7, declination = (-2,5))
    while getattr(thread, "do_run", True):
        thread.data = hmc.degrees(hmc.heading())[0]
        fo = open("/var/www/js/sensors_heading_tmp.html", "wb")
        fo.write("Heading: " + str(thread.data));
        fo.close()
        copyfile("/var/www/js/sensors_heading_tmp.html", "/var/www/js/sensors_heading_current.html")
        time.sleep(.1)

tReadHMC5883L = threading.Thread(target=readHMC5883L)
tReadHMC5883L.start()
#tReadHMC5883L.do_run = False


def readMS5803():
    thread = threading.currentThread()   
    ms5803_14ba = MS5803() 
    while getattr(thread, "do_run", True):
        ms5803 = ms5803_14ba.read()
        thread.mbar = ms5803['mbar']
        fo = open("/var/www/js/sensors_depth_tmp.html", "wb")
        fo.write("Pressure: " + str(thread.mbar) + " mbar");
        fo.close()
        copyfile("/var/www/js/sensors_depth_tmp.html", "/var/www/js/sensors_depth_current.html")
        thread.temp = ms5803['temp']
        fo = open("/var/www/js/sensors_temperature_tmp.html", "wb")
        fo.write("Temperature: " + str(thread.temp));
        fo.close()
        copyfile("/var/www/js/sensors_temperature_tmp.html", "/var/www/js/sensors_temperature.html")
        time.sleep(1)

tReadMS5803 = threading.Thread(target=readMS5803)
tReadMS5803.start()
#tReadMS5803.do_run = False



import RPi.GPIO as G   
G.setmode(G.BCM)

from RPIO import PWM 
PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
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
    G.output(pinSlp, False)
    return



G.setup(pinLED, G.OUT)
time.sleep(1)
G.cleanup(pinLED)
G.setup(pinLED, G.OUT)
time.sleep(1)
G.cleanup(pinLED)


def PID_yaw(heading_target):
    ## parameters for PID control
    K1 = 2
    K2 = 2
    heading_torrence = 5
    ## Initial heading error
    heading_senosr = tReadHMC5883L.data
    ## heading_error_last = heading_target - heading_senosr
    ## create thread;
    thread = threading.currentThread()    
    thread.heading_target = thread.heading_new = heading_target
    propellerStop = False
    ## Start the loop;
    while getattr(thread, "do_run", True):
        if(thread.heading_new != thread.heading_target):
            heading_target = thread.heading_new
            thread.heading_target = thread.heading_new
        if heading_target == -1:
            if propellerStop == False:
            	s.set_servo(pinLft, 1000)
            	s.set_servo(pinRgt, 1000)
            	propellerStop = True
            time.sleep(1)
            ## print("waiting heading_target input every second...")
        else:
            propellerStop == True
            heading_senosr = tReadHMC5883L.data
            if heading_senosr > heading_target:
                heading_error = heading_senosr - heading_target
                if heading_error >= 180:
                    heading_error = 360 - heading_error
                    dirction = "right"
                else:
                    dirction = "left"
            else:
                heading_error =  heading_target - heading_senosr
                if heading_error >= 180:
                    heading_error = 360 - heading_error
                    dirction = "left"
                else:
                    dirction = "right"
            if heading_error > heading_torrence: 
	            if dirction == "right":
	                G.cleanup(pinDlyLft1)
	                G.cleanup(pinDlyLft2)
	                G.cleanup(pinDlyRgt1)
	                G.cleanup(pinDlyRgt2)
	                G.setup(pinDlyLft1, G.OUT)
	                G.setup(pinDlyLft2, G.OUT)
	                s.set_servo(pinLft, heading_error * K2 + 1035)
	                s.set_servo(pinRgt, heading_error * K1 + 1035)
	            if dirction == "left":
	                G.cleanup(pinDlyLft1)
	                G.cleanup(pinDlyLft2)
	                G.cleanup(pinDlyRgt1)
	                G.cleanup(pinDlyRgt2)
	                G.setup(pinDlyRgt1, G.OUT)
	                G.setup(pinDlyRgt2, G.OUT)
	                s.set_servo(pinLft, heading_error * K1 + 1035)
	                s.set_servo(pinRgt, heading_error * K2 + 1035)
	            time.sleep(.5)
            else:
	            s.set_servo(pinLft, 1000)
	            s.set_servo(pinRgt, 1000)
	            time.sleep(.5)


tPID_yaw = threading.Thread(target=PID_yaw, args=(-1,))
tPID_yaw.start()

def PID_yaw(yaw = -1):
	tPID_yaw.heading_new = yaw

def PID_mbar():
    mbar_target = mbar_sensor = 0
    thread = threading.currentThread()    
    thread.mbar_target = thread.mbar_new = mbar_target
    thread.position_0 = 0
    ## Start the loop;
    while getattr(thread, "do_run", True):
        if(thread.mbar_new != thread.mbar_target):
            mbar_target = thread.mbar_new
            thread.mbar_target = thread.mbar_new
        if mbar_target == 0:
            time.sleep(1)
        else:
            mbar_senosr = tReadMS5803.mbar
            print mbar_senosr
            if (mbar_senosr > 1000) & (mbar_senosr < 5000):
                mbar_error_current  = mbar_senosr - mbar_target
                thread.position_1 = mbar_error_current * 2
                if thread.position_1 < -180:
                    thread.position_1 = -180
                elif thread.position_1 > 180:
                    thread.position_1 = 180
                step =  thread.position_1 - thread.position_0
                print step
                thread.position_0 = thread.position_1
                if (step > 1): stepMotor(step)
        time.sleep(1)


tPID_mbar = threading.Thread(target=PID_mbar)
tPID_mbar.start()


def PID_mbar(mbar = 0):
	tPID_mbar.mbar_new = mbar


def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html")])
    i = urlparse.parse_qs(environ["QUERY_STRING"])
    yield ('&nbsp;') 
    #  url = "stp=-300&stp=50&lft=1050&rgt=1100&led=off"
    if "stp" in i:
        stepMotor(int(i["stp"][0]))
    if "yaw" in i:
        PID_yaw(yaw = int(i["yaw"][0]))
    if "mbar" in i:
        PID_mbar(mbar = int(i["mbar"][0]))        
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


# f = open('/var/www/js/sensors.html', 'r+')
# sensorData = f.read()
# f.close()

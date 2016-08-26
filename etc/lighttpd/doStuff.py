#!/usr/bin/pythonRoot

import sys, time, urlparse, smbus, math, threading,struct

from shutil import copyfile

from flup.server.fcgi import WSGIServer 


class MS5803:
    osr = {256:0,512:2,1024:4,2048:6,4096:8}
    def __init__(self,address=0x76,bus=1):
        self.bus = smbus.SMBus(bus)
        self.address = address
        self.reset()
        time.sleep(0.05)
        self._C = self._read_prom()
    def __enter__(self):
        return self
    def __exit__(self,*ignored):
        return True
    def reset(self):
        self.bus.write_byte(self.address,0x1E)
        time.sleep(0.1)
    def read(self,osr=4096):
        D1 = self._raw_pressure(osr=osr)
        D2 = self._raw_temperature(osr=osr)
        C = self._C
        dT = D2 - C[5]*(2**8)
        TEMP = 2000L + dT*C[6]/(2**23)
        OFF = long(C[2])*(2**16) + (long(C[4])*dT)/(2**7)
        SENS = long(C[1])*(2**15) + (long(C[3])*dT)/(2**8)
        if TEMP < 2000:
            T2 = 3*(dT**2)/2**33
            OFF2 = 3*((TEMP - 2000)**2)/2
            SENS2 = 5*((TEMP - 2000)**2)/(2**3) # 2**3 == readability...
            if TEMP < -1500:
                OFF2 = OFF2 + 7*((TEMP + 1500)**2)
                SENS2 = SENS2 + 4*((TEMP + 1500)**2)
        else:
            T2 = 7*(dT**2)/2**37
            OFF2 = ((TEMP-2000)**2)/(2**4)
            SENS2 = 0
        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        # - - -
        P = (long(D1)*SENS/(2**21) - OFF)/(2**15)
        TEMP = TEMP/100.
        P = P/10.
        return {'mbar':P,'temp':TEMP}
    def pretty(self,r=None):
        if r is None:
            r = self.read()
        return '{} kPa, {} Deg.C'.format(r['mbar'],r['temp'])
    def _read_prom(self):
        tmp = [self.bus.read_byte_data(self.address,i) for i in range(0xA0,0xAE+1)]
        C = struct.unpack('>HHHHHHHB',''.join([chr(c) for c in tmp]))
        return C
    def _raw_pressure(self,osr=4096):
        self.bus.write_byte(self.address,0x40 + self.osr[osr])
        time.sleep(0.1)
        tmp = self.bus.read_i2c_block_data(self.address,0,3)
        tmp.insert(0,0)
        D1 = struct.unpack('>I',''.join([chr(c) for c in tmp]))[0]
        return D1
    def _raw_temperature(self,osr=4096):
        self.bus.write_byte(self.address,0x50 + self.osr[osr])
        time.sleep(0.1)
        tmp = self.bus.read_i2c_block_data(self.address,0,3)
        tmp.insert(0,0)
        D2 = struct.unpack('>I',''.join([chr(c) for c in tmp]))[0]
        return D2



class hmc5883l:
    __scales = {
        0.88: [0, 0.73],
        1.30: [1, 0.92],
        1.90: [2, 1.22],
        2.50: [3, 1.52],
        4.00: [4, 2.27],
        4.70: [5, 2.56],
        5.60: [6, 3.03],
        8.10: [7, 4.35],
    }
    def __init__(self, port=1, address=0x1E, gauss=1.3, declination=(0,0)):
        self.bus = smbus.SMBus(port)
        self.address = address
        (degrees, minutes) = declination
        self.__declDegrees = degrees
        self.__declMinutes = minutes
        self.__declination = (degrees + minutes / 60) * math.pi / 180
        (reg, self.__scale) = self.__scales[gauss]
        self.bus.write_byte_data(self.address, 0x00, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(self.address, 0x01, reg << 5) # Scale
        self.bus.write_byte_data(self.address, 0x02, 0x00) # Continuous measurement
    def declination(self):
        return (self.__declDegrees, self.__declMinutes)
    def twos_complement(self, val, len):
        # Convert twos compliment to integer
        if (val & (1 << len - 1)):
            val = val - (1<<len)
        return val
    def __convert(self, data, offset):
        val = self.twos_complement(data[offset] << 8 | data[offset+1], 16)
        if val == -4096: return None
        return round(val * self.__scale, 4)
    def axes(self):
        data = self.bus.read_i2c_block_data(self.address, 0x00)
        #print map(hex, data)
        x = self.__convert(data, 3)
        y = self.__convert(data, 7)
        z = self.__convert(data, 5)
        return (x,y,z)
    def heading(self):
        (x, y, z) = self.axes()
        headingRad = math.atan2(y, x)
        headingRad += self.__declination
        # Correct for reversed heading
        if headingRad < 0:
            headingRad += 2 * math.pi
        # Check for wrap and compensate
        elif headingRad > 2 * math.pi:
            headingRad -= 2 * math.pi
        # Convert to degrees from radians
        headingDeg = headingRad * 180 / math.pi
        return headingDeg
    def degrees(self, headingDeg):
        degrees = math.floor(headingDeg)
        minutes = round((headingDeg - degrees) * 60)
        return (degrees, minutes)
    def __str__(self):
        (x, y, z) = self.axes()
        return "Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n" \
               "Declination: " + self.degrees(self.declination()) + "\n" \
               "Heading: " + self.degrees(self.heading()) + "\n"


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
        time.sleep(.5)

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
    mbar_target = mbar_sensor = 1003
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
                stepMotor(step)
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

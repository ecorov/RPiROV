#!/usr/bin/pythonRoot

import sys, time, urlparse, smbus, math, threading


from flup.server.fcgi import WSGIServer 

class MS5803:
    '''Library for the SparkFun MS5803-12BA Pressure Sensor'''  
    PROM_READ = 0xA2
    _DEFAULT_I2C_ADDRESS = 0x76      
    '''Version 2'''
    # PROM Calibration values stored in the C array
    # C[0]       always equals 0 - not used
    # C[1]       Pressure sensitivy
    # C[2]       Pressure offset
    # C[3]       Temperature coefficient of pressure sensitivity
    # C[4]       Temperature coefficient of pressure offset
    # C[5]       Reference temperature
    # C[6]       Temperature coefficient of the temperature    
    C = []        
    '''Version 1 - working
    # PROM Calibration values stored in the C array
    C1 = 0        #Pressure sensitivy
    C2 = 0        #Pressure offset
    C3 = 0        #Temperature coefficient of pressure sensitivity
    C4 = 0        #Temperature coefficient of pressure offset
    C5 = 0      #Reference temperature
    C6 = 0      #Temperature coefficient of the temperature
    '''    
    def __init__(self, i2cAddress= _DEFAULT_I2C_ADDRESS, bus = 1, *args, **kwargs):
        self.bus = smbus.SMBus(bus)
        self.i2cAddress = i2cAddress
        self.bus.write_quick(i2cAddress)
        # super(MS5803, self).__init__(i2cAddress, *args, **kwargs)        
        # MS5803_14BA address, 0x76(118)
        # 0x1E(30)	Reset command
        # Sent once after power-on
        self.bus.write_byte(i2cAddress, 0x1E)         
        # Let it wake up
        time.sleep(0.1)       
        # ---- Read 12 bytes of calibration data ----        
        '''Version 2 '''
        self.C.append(0)
        for i in range(6):
            data = self.bus.read_i2c_block_data(self.i2cAddress, self.PROM_READ+(i*2), 2)
            self.C.append((data[0] << 8) + data[1])        
        ''' Version 1, Older code - works 
        # Read pressure sensitivity
        data = self.bus.read_i2c_block_data(self.i2cAddress, 0xA2, 2)
        self.C1 = (data[0] << 8) + data[1]      
        # Read pressure offset
        data = self.bus.read_i2c_block_data(self.i2cAddress, 0xA4, 2)
        self.C2 = (data[0] << 8) + data[1]      
        # Read temperature coefficient of pressure sensitivity
        data = self.bus.read_i2c_block_data(self.i2cAddress, 0xA6, 2)
        self.C3 = (data[0] << 8) + data[1]     
        # Read temperature coefficient of pressure offset
        data = self.bus.read_i2c_block_data(self.i2cAddress, 0xA8, 2)
        self.C4 = (data[0] << 8) + data[1]     
        # Read reference temperature
        data = self.bus.read_i2c_block_data(self.i2cAddress, 0xAA, 2)
        self.C5 = (data[0] << 8) + data[1]  
        # Read temperature coefficient of the temperature
        data = self.bus.read_i2c_block_data(self.i2cAddress, 0xAC, 2)
        self.C6 = (data[0] << 8) + data[1]
        '''      
    # Read function, returns a dictionary of the pressure and temperature values      
    def read(self): 
        #---- Read digital pressure and temperature data ----
        # MS5803_14BA address, 0x76(118)
        # 0x48(72)	Pressure conversion(OSR = 4096) command
        self.bus.write_byte(self.i2cAddress, 0x48)       
        time.sleep(0.5)       
        # Read digital pressure value
        # Read data back from 0x00(0), 3 bytes
        # D1 MSB2, D1 MSB1, D1 LSB
        value = self.bus.read_i2c_block_data(self.i2cAddress, 0x00, 3)
        D1 = (value[0] << 16)  + (value[1] << 8) + value[2]      
        # MS5803_14BA address, i2cAddress(118)
        # 0x58(88)	Temperature conversion(OSR = 4096) command
        self.bus.write_byte(self.i2cAddress, 0x58)    
        time.sleep(0.5)  
        # Read digital temperature value
        # Read data back from 0x00(0), 3 bytes
        # D2 MSB2, D2 MSB1, D2 LSB
        value = self.bus.read_i2c_block_data(self.i2cAddress, 0x00, 3)
        D2 = (value[0] << 16)  + (value[1] << 8) + value[2]   
        '''Version 2'''
        # ---- Calculate temperature ----
        dT = D2 - self.C[5] * (2**8)
        TEMP = 2000 + dT * self.C[6] / (2**23)     
        # ---- Calculated temperature compensated pressure ----
        OFF = self.C[2] * (2**16) + (self.C[4] * dT) / (2**7)
        SENS = self.C[1] * (2**15) + (self.C[3] * dT ) / (2**8)    
        '''Version 1 - working
        # ---- Calculate temperature ----
        dT = D2 - self.C5 * (2**8)
        TEMP = 2000 + dT * self.C6 / (2**23)  
        # ---- Calculated temperature compensated pressure ----
        OFF = self.C2 * (2**16) + (self.C4 * dT) / (2**7)
        SENS = self.C1 * (2**15) + (self.C3 * dT ) / (2**8)
        '''
        # Temperature compensated pressure (not the most accurate)
        # Use the flowchart for optimum accuracy
        # Pressure: P = (D1 * SENS / ((2**21) - OFF)) / (2**13)     
        # ---- Second order temperature compensation (flowchart)
        T2 = 0
        OFF2 = 0
        SENS2 = 0   
        if TEMP > 2000 :
            T2 = 7 * (dT * dT)/ (2**37)
            OFF2 = ((TEMP - 2000)**2) / (2**4)
            SENS2= 0
        elif TEMP < 2000 :
       	    T2 = 3 * (dT ** 2) / (2**33)
       	    OFF2 = 3 * ((TEMP - 2000) ** 2) / 2
       	    SENS2 = 5 * ((TEMP - 2000) ** 2) / (2**3)
       	    if TEMP < -1500:
      		OFF2 = OFF2 + 7 * ((TEMP + 1500) ** 2)
      		SENS2 = SENS2 + 4 * ((TEMP + 1500) ** 2)
        TEMP = TEMP - T2
        OFF = OFF - OFF2
        SENS = SENS - SENS2
        pressure = ((((D1 * SENS) / (2**21)) - OFF) / (2**15)) / 10.0
        cTemp = TEMP / 100.0        
        # return values in a dictionary
        return {"mbar" : pressure, "temp": cTemp}


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
        fo = open("/var/www/js/sensors_heading_current.html", "wb")
        fo.write(str(thread.data));
        fo.close()
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
        fo = open("/var/www/js/sensors_depth_current.html", "wb")
        fo.write(str(thread.mbar));
        fo.close()
        thread.temp = ms5803['temp']
        fo = open("/var/www/js/sensors_temperature.html", "wb")
        fo.write(str(thread.temp));
        fo.close()
        time.sleep(5)

tReadMS5803 = threading.Thread(target=readMS5803)
tReadMS5803.start()
#tReadMS5803.do_run = False



#ms5803_14ba = MS5803()
#hmc5883l = hmc5883l(gauss = 4.7, declination = (-2,5))

#hmc5883l.degrees(hmc5883l.heading())[0]
#ms5803 = ms5803_14ba.read()
#mbar = ms5803['mbar']
#temp = ms5803['temp']




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


# f = open('/var/www/js/sensors.html', 'r+')
# sensorData = f.read()
# f.close()

import time 
import smbus

		
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


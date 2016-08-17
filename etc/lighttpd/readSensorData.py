import time
from HMC5883L import hmc5883l
compass = hmc5883l(gauss = 4.7, declination = (-2,5))

while True:
    fo = open("/var/www/js/sensors.html", "wb")
    fo.write("compass:" + str(compass.degrees(compass.heading())[0]));
    fo.close()
    time.sleep(.1)


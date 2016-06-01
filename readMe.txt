
 
Steps:
 1. After burning Rasbian image into RPi's Micro SD card, enable the camera module and extent storage.
sudo raspi-config


Test: 
 cd; sudo rm -R *;  sudo wget https://github.com/withr/RPiROV/archive/master.zip; unzip master.zip; sudo chmod 777 -R RPiROV-master/;cd RPiROV-master/; ./Installer.sh remove; ./Installer.sh install; ./Installer.sh start
 



 
 
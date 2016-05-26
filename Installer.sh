#!/bin/bash

# Copyright (c) 2014, Silvan Melchior
# All rights reserved.

# Redistribution and use, with or without modification, are permitted provided
# that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Neither the name of the copyright holder nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Description
# This script installs a browser-interface to control the RPi Cam. It can be run
# on any Raspberry Pi with a newly installed raspbian and enabled camera-support.
#
# Edited by jfarcher to work with github
# Edited by slabua to support custom installation folder


# Configure below the folder name where to install the software to,
#  or leave empty to install to the root of the webserver.
# The folder name must be a subfolder of /var/www/ which will be created
#  accordingly, and must not include leading nor trailing / character.
# Default upstream behaviour: rpicamdir="" (installs in /var/www/)

case "$1" in

  remove)
        sudo killall raspimjpeg
        #sudo apt-get remove -y apache2 php5 libapache2-mod-php5 gpac motion zip python-flup lighttpd
        #sudo apt-get autoremove -y

        sudo rm -r /var/www/*
        sudo rm /etc/sudoers.d/RPiROV
        sudo rm /usr/bin/raspimjpeg
        sudo rm /etc/raspimjpeg
        sudo cp -r /etc/rc.local.bak /etc/rc.local
        sudo chmod 755 /etc/rc.local

        echo "Removed everything"
        ;;

  autostart_yes)
        sudo cp -r etc/rc_local_run/rc.local /etc/
        sudo chmod 755 /etc/rc.local
        echo "Changed autostart"
        ;;

  autostart_no)
        sudo cp -r /etc/rc.local.bak /etc/rc.local
        sudo chmod 755 /etc/rc.local
        echo "Changed autostart"
        ;;

  install)
        sudo killall raspimjpeg
        git pull origin master
        # sudo apt-get install -y apache2 php5 libapache2-mod-php5 gpac motion zip python-flup lighttpd

        sudo mkdir -p /var/www/media
        sudo cp -r www/* /var/www/
        if [ -e /var/www/index.html ]; then
          sudo rm /var/www/index.html
        fi
        sudo chown -R www-data:www-data /var/www
        
        if [ ! -e /var/www/FIFO ]; then
          sudo mknod /var/www/FIFO p
        fi
        sudo chmod 666 /var/www/FIFO
        
        if [ ! -e /var/www/FIFO1 ]; then
          sudo mknod /var/www/FIFO1 p
        fi
        sudo chmod 666 /var/www/FIFO1
        sudo chmod 755 /var/www/raspizip.sh

        if [ ! -e /var/www/cam.jpg ]; then
          sudo ln -sf /run/shm/mjpeg/cam.jpg /var/www/cam.jpg
        fi

     
        cat etc/apache2/sites-available/default.1 > etc/apache2/sites-available/default
        sudo cp -r etc/apache2/sites-available/default /etc/apache2/sites-available/
        sudo chmod 644 /etc/apache2/sites-available/default
        sudo cp etc/apache2/conf.d/other-vhosts-access-log /etc/apache2/conf.d/other-vhosts-access-log
        sudo chmod 644 /etc/apache2/conf.d/other-vhosts-access-log

        sudo cp etc/sudoers.d/RPiROV /etc/sudoers.d/
        sudo chmod 440 /etc/sudoers.d/RPiROV

        sudo cp -r bin/raspimjpeg /opt/vc/bin/
        sudo chmod 755 /opt/vc/bin/raspimjpeg
        if [ ! -e /usr/bin/raspimjpeg ]; then
          sudo ln -s /opt/vc/bin/raspimjpeg /usr/bin/raspimjpeg
        fi

        cat etc/raspimjpeg/raspimjpeg.1 > etc/raspimjpeg/raspimjpeg
        sudo cp -r /etc/raspimjpeg /etc/raspimjpeg.bak
        sudo cp -r etc/raspimjpeg/raspimjpeg /etc/
        sudo chmod 644 /etc/raspimjpeg
        if [ ! -e /var/www/raspimjpeg ]; then
          sudo ln -s /etc/raspimjpeg /var/www/raspimjpeg
        fi

		sudo mkdir /var/www/html/
		sudo cp etc/lighttpd/doStuff.py /var/www/html/
		sudo cp etc/lighttpd/index.html /var/www/html/
		sudo chmod 755 /var/www/html/doStuff.py
		sudo cp /usr/bin/python2.7 /usr/bin/pythonRoot
		sudo chmod u+s /usr/bin/pythonRoot
		sudo cp etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf

        cat etc/rc_local_run/rc.local.1 > etc/rc_local_run/rc.local
        sudo cp -r /etc/rc.local /etc/rc.local.bak
        sudo cp -r etc/rc_local_run/rc.local /etc/
        sudo chmod 755 /etc/rc.local

        #cat etc/motion/motion.conf.1 > etc/motion/motion.conf
        #sudo cp -r etc/motion/motion.conf /etc/motion/
        #sudo chmod 640 /etc/motion/motion.conf
        #sudo chgrp www-data /etc/motion/motion.conf
        #sudo chmod +rrr /etc/motion/motion.conf 
		
        sudo usermod -a -G video www-data
        if [ -e /var/www/uconfig ]; then
          sudo chown www-data:www-data /var/www/uconfig
        fi

        echo "Installer finished"
        ;;

  update)
        sudo killall raspimjpeg
        git pull origin master
        sudo apt-get install -y zip

        sudo cp -r bin/raspimjpeg /opt/vc/bin/
        sudo chmod 755 /opt/vc/bin/raspimjpeg
        sudo cp -r www/* /var/www/

        if [ ! -e /var/www/raspimjpeg ]; then
          sudo ln -s /etc/raspimjpeg /var/www/raspimjpeg
        fi
        sudo chmod 755 /var/www/raspizip.sh

        echo "Update finished"
        ;;

  start)
        ./$0 stop
        sudo mkdir -p /dev/shm/mjpeg
        sudo chown www-data:www-data /dev/shm/mjpeg
        sudo chmod 777 /dev/shm/mjpeg
        sleep 1;sudo su -c 'raspimjpeg > /dev/null &' www-data
        sleep 1;sudo su -c 'php /var/www/schedule.php > /dev/null &' www-data
		killall -9 python lighttpd
		sudo /etc/init.d/lighttpd start
        echo "Started"
        ;;

  debug)
        ./$0 stop
        sudo mkdir -p /dev/shm/mjpeg
        sudo chown www-data:www-data /dev/shm/mjpeg
        sudo chmod 777 /dev/shm/mjpeg
        sleep 1;sudo su -c 'raspimjpeg &' www-data
        sleep 1;sudo sudo su -c 'php /var/www/schedule.php &' www-data
        echo "Started with debug"
        ;;

  stop)
        sudo killall raspimjpeg
        sudo killall php
        sudo killall motion
        echo "Stopped"
        ;;

  *)
        echo "No or invalid option selected"
        ;;

esac


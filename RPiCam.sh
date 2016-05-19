#!/bin/bash

case "$1" in
  remove)
    sudo killall raspimjpeg
    sudo apt-get remove -y apache2 php5 libapache2-mod-php5 gpac motion zip
    sudo apt-get autoremove -y
    sudo rm -r /var/www/*
    sudo rm /etc/sudoers.d/RPI_Cam_Web_Interface
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
    sudo apt-get install -y apache2 php5 libapache2-mod-php5 gpac motion zip
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

    sudo cp etc/sudoers.d/RPI_Cam_Web_Interface /etc/sudoers.d/
    sudo chmod 440 /etc/sudoers.d/RPI_Cam_Web_Interface

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

    cat etc/rc_local_run/rc.local.1 > etc/rc_local_run/rc.local
    sudo cp -r /etc/rc.local /etc/rc.local.bak
    sudo cp -r etc/rc_local_run/rc.local /etc/
    sudo chmod 755 /etc/rc.local

    cat etc/motion/motion.conf.1 > etc/motion/motion.conf
    sudo cp -r etc/motion/motion.conf /etc/motion/
    sudo chmod 640 /etc/motion/motion.conf
    sudo chgrp www-data /etc/motion/motion.conf
    sudo chmod +rrr /etc/motion/motion.conf    
    sudo usermod -a -G video www-data
    if [ -e /var/www/uconfig ]; then
      sudo chown www-data:www-data /var/www/uconfig
    fi
    echo "Installer finished"
    ;;

  start)
    ./$0 stop
    sudo mkdir -p /dev/shm/mjpeg
    sudo chown www-data:www-data /dev/shm/mjpeg
    sudo chmod 777 /dev/shm/mjpeg
    sleep 1;sudo su -c 'raspimjpeg > /dev/null &' www-data
    sleep 1;sudo su -c 'php /var/www/schedule.php > /dev/null &' www-data
    echo "Started"
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


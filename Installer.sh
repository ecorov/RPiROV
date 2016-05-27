#!/bin/bash


case "$1" in

  remove)
        sudo killall raspimjpeg
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
        sudo apt-get install -y apache2 php5 libapache2-mod-php5 gpac 

        sudo cp -r www/* /var/www/
        sudo chown -R www-data:www-data /var/www
        

        sudo mknod /var/www/FIFO p
        sudo chmod 666 /var/www/FIFO
        sudo mknod /var/www/FIFO1 p
        sudo chmod 666 /var/www/FIFO1

        sudo chmod 755 /var/www/raspizip.sh
        sudo ln -sf /run/shm/mjpeg/cam.jpg /var/www/cam.jpg


        sudo cp -r etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf
        sudo /etc/init.d/apache2 restart



        sudo cp etc/sudoers.d/RPiROV /etc/sudoers.d/
        sudo chmod 440 /etc/sudoers.d/RPiROV

        sudo cp -r bin/raspimjpeg /opt/vc/bin/
        sudo chmod 755 /opt/vc/bin/raspimjpeg
        sudo ln -s /opt/vc/bin/raspimjpeg /usr/bin/raspimjpeg


        cat etc/raspimjpeg/raspimjpeg.1 > etc/raspimjpeg/raspimjpeg
        sudo cp -r etc/raspimjpeg/raspimjpeg /etc/
        sudo chmod 644 /etc/raspimjpeg
        sudo ln -s /etc/raspimjpeg /var/www/raspimjpeg


        cat etc/rc_local_run/rc.local.1 > etc/rc_local_run/rc.local
        sudo cp -r /etc/rc.local /etc/rc.local.bak
        sudo cp -r etc/rc_local_run/rc.local /etc/
        sudo chmod 755 /etc/rc.local		
        sudo usermod -a -G video www-data


        sudo apt-get install -y python-flup lighttpd
        sudo mkdir /var/www/html/
        sudo cp etc/lighttpd/doStuff.py /var/www/html/
        sudo cp etc/lighttpd/index.html /var/www/html/
        sudo chmod 755 /var/www/html/doStuff.py
        sudo cp /usr/bin/python2.7 /usr/bin/pythonRoot
        sudo chmod u+s /usr/bin/pythonRoot
        sudo cp etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf
        sudo service lighttpd restart
        

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
        # sudo killall motion
        echo "Stopped"
        ;;

  *)
        echo "No or invalid option selected"
        ;;

esac


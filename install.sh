#!/bin/bash

RUNDIR=`pwd`

echo 
echo "Installing the NetKiss program"

# install system prereqs
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip -y
sudo pip3 install --upgrade setuptools

# install python prerequisites
#is pip installed?
pip3 install pyzmq flask waitress

# run python install tasks
python3 ./installer.py

# create @reboot command
(crontab -l ; echo "@reboot sleep 20 && /home/"$USER"/netkiss/run.sh &") | uniq - | crontab -

# do any networking to open ports?

# Make run.sh executable
cd $RUNDIR
chmod +x ./run.sh
chmod +x ./update.sh


echo "Please reboot to apply changes"
echo "Server will start on boot"
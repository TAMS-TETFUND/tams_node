#!/bin/bash

sudo apt-get install -y build-essential
sudo apt-get install -y cmake
sudo apt-get install -y gfortran
sudo apt-get install -y git
sudo apt-get install -y wget
sudo apt-get install -y curl
sudo apt-get install -y graphicsmagick
sudo apt-get install -y libgraphicsmagick1-dev
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libavcodec-dev
sudo apt-get install -y libavformat-dev
sudo apt-get install -y libboost-all-dev
sudo apt-get install -y libgtk2.0-dev
sudo apt-get install -y libjpeg-dev
sudo apt-get install -y liblapack-dev
sudo apt-get install -y libswscale-dev
sudo apt-get install -y pkg-config
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-numpy
sudo apt-get install -y python3-pip
sudo apt-get install -y zip
sudo apt-get -y clean

sudo apt-get install -y  python3-picamera
sudo pip3 install --upgrade -y picamera[array]

sudo touch /etc/dphys-swapfile

sudo sed -i s'/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile

pip install dlib

sudo sed -i s'/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/' /etc/dphys-swapfile

pip3 install numpy
pip3 install scikit-image
sudo apt-get install python3-scipy
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install python3-pyqt5
sudo apt install libqt4-test
pip3 install opencv-python==3.4.6.27
pip3 install face_recognition 
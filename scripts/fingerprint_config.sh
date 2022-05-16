sudo echo "#Disable Bluetooth" >> /boot/config.txt
sudo echo "dtoverlay=disable-bt" >> /boot/config.txt

sudo systemctl disable hciuart.service
sudo systemctl disable bluealsa.service
sydo systemctl disable bluetooth.service

sudo echo "Please restart the PI now!"
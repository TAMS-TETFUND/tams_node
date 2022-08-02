#!/bin/bash
sudo apt install network-manager network-manager-gnome

# Configure dhcpcd to ignore wlan0
sudo echo "denyinterfaces wlan0" >> /etc/dhcpcd.conf

# Configure Network manager to control wlan0 and assume dhcp duties
# add the following to /etc/NetworkManager/NetworkManager.conf

# [main]
# plugins=ifupdown,keyfile
# dhcp=internal

# [ifupdown]
# managed=true


# Finally, reboot
# sudo reboot
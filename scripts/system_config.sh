#!/bin/bash
sudo apt-get install -y hostapd
sudo apt-get install -y dnsmasq


sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

sudo touch /etc/dhcpcd.conf

sudo echo $'\ninterface wlan0' >> /etc/dhcpcd.conf
sudo echo $'static ip_address=192.168.22.10/24' >> /etc/dhcpc.conf
sudo echo $'denyinterfaces eth0' >> /etc/dhcpc.conf
sudo echo $'denyinterfaces wlan0' >> /etc/dhcpc.conf

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo touch /etc/dnsmasq.conf

sudo echo $'\ninterface=wlan0' >> /etc/dnsmasq.conf
sudo echo $'  dhcp-range=192.168.22.11,192.168.22.30,255.255.255.0,24h' >> /etc/dnsmasq.conf

sudo touch /etc/hostapd/hostapd.conf

sudo echo $'\ninterface=wlan0' >> /etc/hostapd/hostapd.conf
sudo echo $'bridge=br0' >> /etc/hostapd/hostapd.conf
sudo echo $'hw_mode=g' >> /etc/hostapd/hostapd.conf
sudo echo $'channel=7' >> /etc/hostapd/hostapd.conf
sudo echo $'wmm_enabled=0' >> /etc/hostapd/hostapd.conf
sudo echo $'macaddr_acl=0' >> /etc/hostapd/hostapd.conf
sudo echo $'auth_algs=1' >> /etc/hostapd/hostapd.conf
sudo echo $'ignore_broadcast_ssid=0' >> /etc/hostapd/hostapd.conf
sudo echo $'wpa=2' >> /etc/hostapd/hostapd.conf
sudo echo $'wpa_key_mgmt=WPA-PSK' >> /etc/hostapd/hostapd.conf
sudo echo $'wpa_pairwise=CCMP' >> /etc/hostapd/hostapd.conf
sudo echo $'ssid=tams' >> /etc/hostapd/hostapd.conf
sudo echo $'wpa_passphrase=tams1234' >> /etc/hostapd/hostapd.conf

sudo touch /etc/default/hostapd

sudo sed -i s'/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/' /etc/default/hostapd

sudo touch /etc/sysctl.conf

sudo sed -i s'/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1' /etc/sysctl.conf

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

sudo touch /etc/rc/local
sudo sed -i '/exit 0/i iptables-restore < /etc/iptables.ipv4.nat' /etc/rc/local


sudo apt-get install -y bridge-utils
sudo brctl addbr br0
sudo brctl addif br0 eth0

sudo touch /etc/network/interfaces

sudo echo $'\nauto br0' >> /etc/network/interfaces
sudo echo $'iface br0 inet manual' >> /etc/network/interfaces
sudo echo $'bridge_ports eth0 wlan0' >> /etc/network/interfaces

sudo echo "Done. Please restart your raspberry PI now!"
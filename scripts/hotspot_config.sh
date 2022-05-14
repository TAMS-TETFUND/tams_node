#!/bin/bash

sudo apt install -y hostapd

sudo systemctl unmask hostapd
sudo systemctl enable hostapd

sudo apt install -y dnsmasq

sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

sudo touch /etc/dhcpcd.conf

sudo echo "interface wlan0" >> /etc/dhcpcd.conf
sudo echo "  static ip_address=192.168.4.1/24" >> /etc/dhcpcd.conf
sudo echo "  nohook wpa_supplicant" >> /etc/dhcpcd.conf

sudo touch /etc/sysctl.d/routed-ap.conf

sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.d/routed-ap.conf

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

sudo netfilter-persistent save

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

sudo touch /etc/dnsmasq.conf

sudo echo "interface=wlan0" >> /etc/dnsmasq.conf
sudo echo "dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf
sudo echo "domain=wlan" >> /etc/dnsmasq.conf
sudo echo "address=/gw.wlan/192.168.4.1" >> /etc/dnsmasq.conf

sudo touch /etc/hostapd/hostapd.conf

sudo echo "interface=wlan0" >> /etc/hostapd.conf
sudo echo "ssid=tams01" >> /etc/hostapd.conf
sudo echo "hw=mode=g" >> /etc/hostapd.conf
sudo echo "channel=7" >> /etc/hostapd.conf
sudo echo "macaddr_acl=0" >> /etc/hostapd.conf
sudo echo "auth_algs=1" >> /etc/hostapd.conf
sudo echo "ignore_broadcast_ssid=0" >> /etc/hostapd.conf
sudo echo "wpa=2" >> /etc/hostapd.conf
sudo echo "wpa_passphrase=tams01" >> /etc/hostapd.conf
sudo echo "wpa_key_mgmt=WPA-PSK" >> /etc/hostapd.conf
sudo echo "wpa_pairwise=TKIP" >> /etc/hostapd.conf
sudo echo "rsn_pairwise=CCMP" >> /etc/hostapd.conf

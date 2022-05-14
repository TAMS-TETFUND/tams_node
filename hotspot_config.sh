#!/bin/bash

sudo apt install -y hostapd

sudo systemctl unmask hostapd
sudo systemctl enable hostapd

sudo apt install -y dnsmasq

sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

touch /etc/dhcpcd.conf

echo "interface wlan0" >> /etc/dhcpcd.conf
echo "  static ip_address=192.168.4.1/24" >> /etc/dhcpcd.conf
echo "  nohook wpa_supplicant" >> /etc/dhcpcd.conf

touch /etc/sysctl.d/routed-ap.conf

echo "net.ipv4.ip_forward=1"

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

sudo netfilter-persistent save

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

touch /etc/dnsmasq.conf

echo "interface=wlan0" >> /etc/dnsmasq.conf
echo "dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf
echo "domain=wlan" >> /etc/dnsmasq.conf
echo "address=/gw/wlan/192.168.4.1" >> /etc/dnsmasq.conf

touch /etc/hostapd/hostapd.conf

echo "interface=wlan0" >> /etc/hostapd.conf
echo "ssid=tams01" >> /etc/hostapd.conf
echo "hw=mode=g" >> /etc/hostapd.conf
echo "channel=7" >> /etc/hostapd.conf
echo "auth_algs=1" >> /etc/hostapd.conf
echo "ignore_broadcast_ssid=0" >> /etc/hostapd.conf
echo "wpa=2" >> /etc/hostapd.conf
echo "wpa_passphrase=tams01" >> /etc/hostapd.conf
echo "wpa_key_mgmt" >> /etc/hostapd.conf
echo "wpa_pairwise=TKIP" >> /etc/hostapd.conf
echo "rsn_pairwise=CCMP" >> /etc/hostapd.conf

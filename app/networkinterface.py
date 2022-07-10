"""This module will handle the connection of node devices
to networks: wifi, LORA, etc.

"""
import os


def connect_to_wifi(ssid, network_password):
    """
    This function will handle establishment connection to WiFi networks
    

    returns: 
        0 on successful connection
        2560 if unsuccessful
    """
    try:
        message = os.system('nmcli device wifi connect "' + ssid + '" password "' + network_password + '"')
    except Exception as e:
        return "Connection to %s failed: %s" % ssid, e.args
    else:
        return message

def connect_to_LORA():
    """This function will handle connection to LORA."""
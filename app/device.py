"""This module provides general device information like 
device name and hardware specifications."""
import os

def os_name():
    return os.uname().sysname


def wlan_interface_name():
    os_uname = os.uname()
    if os_uname.sysname == 'Linux':
        if 'ubuntu' in os_uname.version.lower():
            return 'wlo1'
        else:
            return 'wlan0'
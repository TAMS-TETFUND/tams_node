"""This module provides general device information like 
device name and hardware specifications."""
import os
from typing import Optional


def os_name() -> str:
    """Return the name of the OS of host computer."""
    return os.uname().sysname


def wlan_interface_name() -> Optional[str]:
    """Return name of the wireless lan interface on host computer.
    
    TODO: current implementation only supports a subset of Unix OS's
    """
    os_uname = os.uname()
    if os_uname.sysname == "Linux":
        if "ubuntu" in os_uname.version.lower():
            return "wlo1"
        else:
            return "wlan0"

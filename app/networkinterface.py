"""This module will handle the connection of node devices
to networks: wifi, LORA, etc.
"""
import os
import subprocess
from typing import Any, List, Optional, Tuple, Union

from app.device import wlan_interface_name


def connect_to_LORA() -> None:
    """This function will handle connection to LORA."""
    pass


class WLANInterface:
    """A class to manage WLAN communication in application."""

    @classmethod
    def connect_to_wifi(
        cls, ssid: str, network_password: str
    ) -> Union[int, Tuple[Any, ...]]:
        """Establish connection to a WiFi network.

        returns:
            0 on successful connection
            2560 if unsuccessful
        """

        if cls.is_connected():
            if cls.current_network_name() == ssid:
                return 0
        try:
            message = os.system(
                'nmcli device wifi connect "'
                + ssid
                + '" password "'
                + network_password
                + '"'
            )
        except Exception as e:
            return "Connection to %s failed: %s" % ssid, e.args
        else:
            return message

    @staticmethod
    def available_networks() -> List[str]:
        """Checks for available WiFi networks."""
        network_query = subprocess.run(
            "iwlist scan", shell=True, capture_output=True
        ).stdout
        available_networks = [
            el.strip().split(":")[1].replace('"', "")
            for el in network_query.decode("utf8").split("\n")
            if "ESSID" in el
        ]
        return available_networks

    @staticmethod
    def connection_query() -> List[str]:
        """Get information about the wireless interface of the device.

        Returns a list of detailed information about the wireless
        interface of the device. Method returns an empty list if
        the WLAN interface is disabled/unavailable.
        """
        interface_name = wlan_interface_name()
        connection_state_query = (
            subprocess.run(
                "nmcli device show " + interface_name,
                shell=True,
                capture_output=True,
            )
            .stdout.decode("utf8")
            .split("\n")
        )
        return connection_state_query

    @classmethod
    def find_parameter(cls, parameter: str) -> Optional[str]:
        """
        This method will search the result of the connection_query
        method for a specified parameter.
        Returns: the value of the parameter if it exists
        else it return None.
        """
        for el in cls.connection_query():
            if parameter in el:
                return el.split(":")[1].strip()
        return None

    @classmethod
    def is_connected(cls) -> bool:
        """Checks if the device is currently connected to a WLAN network"""
        connection_state = cls.find_parameter("GENERAL.STATE")

        if connection_state == "100 (connected)":
            return True
        else:
            return False

    @classmethod
    def current_network_name(cls) -> Optional[str]:
        """Check name of network the device is currently connected to.

        Returns name of network device is currently connected to.
        Returns None if the device is not connected.
        """
        network_name = cls.find_parameter("GENERAL.CONNECTION")
        if network_name == "--":
            return None
        else:
            return network_name

    @classmethod
    def device_ip_address(cls) -> Optional[str]:
        """Check IP address currently assigned to device's WLAN interface.

        Returns the IP address assigned to currently assigned to the
        device's WLAN interface.
        Returns None if the device is not connected to a WLAN network.
        """
        if cls.is_connected():
            ip_address = cls.find_parameter("IP4.ADDRESS[1]")
            if ip_address is None:
                raise RuntimeError("Something went wrong")
            return ip_address.split("/")[0]
        else:
            return None

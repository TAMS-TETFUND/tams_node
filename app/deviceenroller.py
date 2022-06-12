import os
from pathlib import Path
import requests

from appconfigparser import AppConfigParser


class DeviceEnroller:
    """This class will be responsible for the registration of a node device
    and managing the device information:
        -   providing the device id for creating new attendance sessions
        -   providing the device token for authentication when connecting to
            the server for synchronization
    """

    DEVICE_CONFIG_FILE_PATH = os.path.join(
        Path(os.path.abspath(__file__)).parent, ".device_config.ini"
    )
    device_config = AppConfigParser(file_path=DEVICE_CONFIG_FILE_PATH)

    def __init__(self) -> None:
        pass

    @classmethod
    def register(cls, device_registration_url):
        try:
            response = requests.post(url=device_registration_url)
            # the construction of this request is tightly coupled with
            # the implementation of the NodeDeviceList api view on the server application
        except ConnectionError as e:
            raise e

        if response.status_code != 201:
            raise Exception("Error registering device")

        if cls.is_device_registered:
            raise Exception("Device already registered")

        cls.device_config["device_registration"] = dict(response.json())
        return

    @classmethod
    def is_device_registered(cls):
        if cls.device_config.has_section("device_registration"):
            return True
        else:
            return False

    @property
    def device_id(self):
        if not self.is_device_registered():
            raise Exception("Device not registered")
        if not self.device_config.has_option(
            "device_registration", "device_id"
        ):
            raise Exception("Device improperly configured")
        return self.device_config.getint("device_registration", "device_id")

    @property
    def device_name(self):
        if not self.is_device_registered():
            raise Exception("Device not registered")
        if not self.device_config.has_option(
            "device_registration", "device_name"
        ):
            raise Exception("Device improperly configured")
        return self.device_config.get("device_registration", "device_name")

    @property
    def device_token(self):
        if not self.is_device_registered():
            raise Exception("Device not registered")
        if not self.device_config.has_option(
            "device_registration", "device_token"
        ):
            raise Exception("Device improperly configured")
        return self.device_config.get("device_registration", "device_token")

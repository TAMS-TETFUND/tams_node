import json
import os
from pathlib import Path
import requests

from app.serverconnection import ServerConnection
from db.models import NodeDevice


class DeviceRegistration:
    """Class responsible for initial configuration of the node device.

    It will connect the device to the server and obtain a device ID and token to be
    used for subsequent operations like synching to/from the server.
    The obtained token will also be appended to the every attendance info that will
    be sent to the server.
    """

    config_file = os.path.join(
        Path(os.path.abspath(__file__)).parent, ".init_device_config.ini"
    )

    @classmethod
    def register_device(
        cls,
        registration_endpoint: str = "api/v1/node-devices/",
    ) -> bool:
        """Register a node device on the server.

        Returns:
            True if device registration was successful.
            False if device registration fails.
        """
        server_conn = ServerConnection()
        if cls.is_registered():
            raise RuntimeError("Device is already registered.")

        response = requests.post("%s/%s" % (server_conn.server_url, registration_endpoint))
        if response.status == 201:
            device_details = json.loads(response.data.decode("utf-8"))
            if "token" in device_details:
                NodeDevice.objects.create(**device_details)
                return True
        return False

    @classmethod
    def is_registered(cls) -> bool:
        """Confirm a node devices has been registered to the server."""
        device_registration = NodeDevice.objects.all()

        if device_registration.exists():
            return True
        else:
            return False

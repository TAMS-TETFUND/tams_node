import json
import os
from pathlib import Path
import urllib3

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
        server_connection: ServerConnection,
        registration_url: str = "api/v1/node-devices/",
    ) -> bool:
        """Register a node device on the server.
        
        Returns:
            True if device registration was successful.
            False if device registration fails.
        """
        if cls.is_registered():
            raise RuntimeError("Device is already registered.")

        response = urllib3.PoolManager().request(
            "POST",
            "http://%s:%s/%s"
            % (
                server_connection.server_address,
                server_connection.server_port,
                registration_url,
            ),
        )
        if response.status == 201:
            device_details = json.loads(response.data.decode("utf-8"))
            print(type(device_details))

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

import json
import os
from pathlib import Path
import urllib3

from app.serverconnection import ServerConnection
from db.models import NodeDevice

class DeviceRegistration:
    """This class will be responsible for initial configuration of the node device.
    It will connect the device to the server and obtain a device ID and token to be
    used for subsequent operations like synching to/from the server.
    It will also be appended to the every attendance info that will be sent to the server
    - Connect the device to the server = handled by the networkinterface.py module
    - access the registraton api point on the server: This api point will require
        authentication to be accessed.
    - obtain the device details: token and id
    - log obtained device details in a config file
    """
    config_file = os.path.join(Path(os.path.abspath(__file__)).parent, ".init_device_config.ini")

    @classmethod
    def register_device(cls, server_connection: ServerConnection, registration_url="api/v1/node-devices/"):
        """This method will be responsible for registering device on the server."""
        if cls.is_registered():
            raise RuntimeError("Device is already registered.")

        response = urllib3.PoolManager().request('POST', 'http://%s:%s/%s' % (server_connection.server_address, server_connection.server_port, registration_url))
        if response.status == 201:
            device_details = json.loads(response.data.decode('utf-8'))
            print(type(device_details))

            if 'token' in device_details:
                NodeDevice.objects.create(**device_details)
                return True
        return False

    @classmethod
    def is_registered(cls):
        device_registration = NodeDevice.objects.all()
        
        if device_registration.exists():
            return True
        else:
            return False
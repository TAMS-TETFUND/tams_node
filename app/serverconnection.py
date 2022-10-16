from typing import Any, Dict, Optional, TypeVar
from requests import HTTPError
import urllib3
import requests

import app.appconfigparser
from db.models import NodeDevice

app_config = app.appconfigparser.AppConfigParser()


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args: Any, **kwargs: Any):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class ServerConnection(metaclass=SingletonType):
    """Class responsible for managing connection to the TAMS server."""

    _server_protocol: str = "http"
    _server_port: Optional[int] = None
    _server_address: Optional[str] = None

    def __init__(
        self,
        server_address: Optional[str] = None,
        server_port: Optional[int] = None,
    ) -> None:
        self.token: Optional[str] = None
        if server_address is not None:
            self.server_address = server_address
        elif app_config.cp.has_option("server_details", "server_ip_address"):
            self.server_address = app_config.cp.get(
                "server_details", "server_ip_address"
            )
        if server_port is not None:
            self.server_port = server_port
        elif app_config.cp.has_option("server_details", "server_port"):
            self.server_port = app_config.cp.getint(
                "server_details", "server_port"
            )

    def token_authentication(
        self,
        username: str,
        password: str,
        login_endpoint: str = "api/v1/token/login",
    ) -> bool:
        """Authenticate the node device on the server.

        Returns:
            true if authentication is successful and saves obtained
                token to self.token
            else, raise error
        """
        response = urllib3.PoolManager().request(
            "POST",
            "%s/%s" % (self.server_url, login_endpoint),
            fields={"username": username, "password": password},
        )
        if response.status == 200:
            return True
        else:
            raise ConnectionError("Connection error (%s)." % response.status)

    @property
    def server_address(self) -> str:
        """Server IP address."""
        return self._server_address

    @server_address.setter
    def server_address(self, value) -> None:
        """Set server IP address."""
        self._server_address = value

    @property
    def server_port(self) -> int:
        """Server port number."""
        return self._server_port

    @server_port.setter
    def server_port(self, value) -> None:
        """Set server port number."""
        try:
            self._server_port = int(value)
        except TypeError as e:
            e.args = ["Server port number must be an integer"]
            raise e

    @property
    def server_protocol(self):
        """The protocol used in sending requests to server."""
        return self._server_protocol

    @server_protocol.setter
    def server_protocol(self, protocol: str):
        """Set the server protocol."""
        self._server_protocol = protocol

    @property
    def server_url(self):
        """Get the server url."""
        if self.server_address is None or self.server_port is None:
            raise ValueError("Server address and/or port not set")
        return "%s://%s:%s" % (
            self.server_protocol,
            self.server_address,
            self.server_port,
        )

    @property
    def request_header(self) -> Dict[str, str]:
        """Get header for sending requests to server."""
        node = NodeDevice.objects.all().first()

        if node is None:
            raise HTTPError('{"detail": "Device not registered!"}')

        return {
            "Content-Type": "application/json",
            "Authorization": f"NodeToken {node.token} {node.id}",
        }

    def get_token(self) -> str:
        """Get auth token."""
        if self.token is None:
            raise RuntimeError("Unathenticated Request")
        return self.token

    def is_authenticated(self) -> bool:
        """Check if node device has been authenticated."""
        if self.token:
            return True
        else:
            return False

    def test_connection(self) -> bool:
        """Check if server is reachable with provided information."""
        try:
            response = self.request("", get=True)
        except Exception:
            return False
        if response.status_code == 200:
            return True
        return False

    def request(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        headers: Dict[str, str] = {},
        get: bool = False,
        put: bool = False,
    ) -> requests.Response:
        """Make a request to the server."""
        url = "".join([self.server_url, "/", endpoint])
        headers = headers if headers else self.request_header
        try:
            if get:
                res = requests.get(url, headers=headers)
            elif put:
                res = requests.put(url, headers=headers, json=data)
            else:
                res = requests.post(url, headers=headers, json=data)
        except requests.exceptions.RequestException as e:
            raise HTTPError('{"detail": "Connection refused!"}')

        if res.status_code not in range(200, 300):
            raise HTTPError(
                '{"detail": "Connection error (%s): %s"}'
                % (res.status_code, res.reason)
            )

        return res

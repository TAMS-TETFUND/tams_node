import json
import urllib3


class ServerConnection:
    """
    This class will be responsible for establishing connection to the 
    TAMS server.
    """

    def __init__(self):
        self.token = None

    def token_authentication(
        self,
        server_address: str,
        server_port: str,
        username: str,
        password: str,
        login_url: str = "api/v1/token/login"
    ):
        """This method will be responsible for authenticating the
        the node device on the server.

        Returns: true if authentication is successful and saves obtained
            token to self.token
        else: raise error
        """
        response = urllib3.PoolManager().request(
            "POST",
            "http://%s:%s/%s" % (server_address, server_port, login_url),
            fields={"username": username, "password": password},
        )
        if response.status == 200:
            self.token = json.loads(response.data.decode('utf-8'))['auth_token']
            
            # saving the server address details after authentication
            self.server_address = server_address
            self.server_port = server_port         
            return True
        else:
            raise ConnectionError("Connection error (%s)." % response.status)
    
    def get_token(self):
        if self.token is None:
            raise RuntimeError("Unathenticated Request")
        return self.token
    
    def is_authenticated(self):
        if self.token:
                return True
        else:
            return False
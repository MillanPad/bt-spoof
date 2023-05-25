
from nOBEX.client import Client
from nOBEX.bluez_helper import find_service
from nOBEX import headers

class OPPClient(Client):
    def __init__(self, address, port=None):
        if port is None:
            port = find_service("opush", address)
        super(OPPClient, self).__init__(address, port)

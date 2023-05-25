

from nOBEX.client import Client
from nOBEX.bluez_helper import find_service
from nOBEX import headers

class FTPClient(Client):


    def __init__(self, address, port=None):
        if port is None:
            port = find_service("ftp", address)
        super(FTPClient, self).__init__(address, port)

    def connect(self):
        uuid = b"\xF9\xEC\x7B\xC4\x95\x3C\x11\xd2\x98\x4E\x52\x54\x00\xDC\x9E\x09"
        super(FTPClient, self).connect(header_list = [headers.Target(uuid)])

    def capability(self):


        hdrs, data = self.get(header_list=[headers.Type(b"x-obex/capability")])
        return data

class SyncClient(Client):
    def connect(self, header_list=(headers.Target(b"IRMC-SYNC"),)):
        super(SyncClient, self).connect(header_list)

class SyncMLClient(Client):
    def connect(self, header_list=(headers.Target(b"SYNCML-SYNC"),)):
        super(SyncMLClient, self).connect(header_list)


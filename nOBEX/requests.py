

import struct
from nOBEX.common import OBEX_Version, Message, MessageHandler

class Request(Message):
    format = ""

    def __init__(self, data = (), header_data = ()):
        Message.__init__(self, data, header_data)
        self.minimum_length = self.length(Message.format + self.format)

    def is_final(self):
        return (self.code & 0x80) == 0x80

class Connect(Request):
    code = OBEX_Connect = 0x80
    format = "BBH"

    def read_data(self, data):
        # Extract the connection data from the complete data.
        extra_data = data[self.length(Message.format):self.minimum_length]

        obex_version, flags, max_packet_length = struct.unpack(
                ">" + self.format, extra_data)

        self.obex_version = OBEX_Version().from_byte(obex_version)
        self.flags = flags
        self.max_packet_length = max_packet_length

        Request.read_data(self, data)

class Disconnect(Request):
    code = OBEX_Disconnect = 0x81
    format = ""

class Put(Request):
    code = OBEX_Put = 0x02
    format = ""

class Put_Final(Put):
    code = OBEX_Put_Final = 0x82
    format = ""

class Get(Request):
    code = OBEX_Get = 0x03
    format = ""

class Get_Final(Get):
    code = OBEX_Get_Final = 0x83
    format = ""

class Set_Path(Request):
    code = OBEX_Set_Path = 0x85
    format = "BB"
    NavigateToParent = 1
    DontCreateDir = 2

    def read_data(self, data):
        # Extract the extra message data from the complete data.
        extra_data = data[self.length(Message.format):self.minimum_length]

        flags, constants = struct.unpack(">"+self.format, extra_data)

        self.flags = flags
        self.constants = constants

        Request.read_data(self, data)

class Abort(Request):
    code = OBEX_Abort = 0xff
    format = ""

class UnknownRequest(Request):
    def __init__(self, code, data):
        self.code = code
        self.data = data[3:]

class RequestHandler(MessageHandler):
    OBEX_User_First = 0x10
    OBEX_User_Last = 0x1f

    message_dict = {
            Connect.code: Connect,
            Disconnect.code: Disconnect,
            Put.code: Put,
            Put_Final.code: Put_Final,
            Get.code: Get,
            Get_Final.code: Get_Final,
            Set_Path.code: Set_Path,
            Abort.code: Abort
    }

    UnknownMessageClass = UnknownRequest

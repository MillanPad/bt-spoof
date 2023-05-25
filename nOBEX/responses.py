import struct
from nOBEX.common import OBEX_Version, Message, MessageHandler

class Response(Message):
    format = ""

    def __init__(self, data = (), header_data = ()):
        Message.__init__(self, data, header_data)
        self.minimum_length = self.length(Message.format + self.format)

class FailureResponse(Response):
    pass

class Continue(Response):
    code = OBEX_Continue = 0x90

class Success(Response):
    code = OBEX_OK = OBEX_Success = 0xA0

class ConnectSuccess(Success):
    format = "BBH"

class Bad_Request(FailureResponse):
    code = OBEX_Bad_Request = 0xC0

class Unauthorized(FailureResponse):
    code = OBEX_Unauthorized = 0xC1

class Forbidden(FailureResponse):
    code = OBEX_Forbidden = 0xC3

class Not_Found(FailureResponse):
    code = OBEX_Not_Found = 0xC4

class Precondition_Failed(FailureResponse):
    code = OBEX_Precondition_Failed = 0xCC

class UnknownResponse(Response):
    def __init__(self, code, data):
        self.code = code
        self.data = data[3:]

    def __repr__(self):
        return "%s(code=0x%02X, data=%s" % (
                type(self).__name__, self.code, repr(self.data))


class ResponseHandler(MessageHandler):
    message_dict = {
            Continue.code: Continue,
            Success.code: Success,
            Bad_Request.code: Bad_Request,
            Unauthorized.code: Unauthorized,
            Forbidden.code: Forbidden,
            Not_Found.code: Not_Found,
            Precondition_Failed.code: Precondition_Failed
    }

    UnknownMessageClass = UnknownResponse

    def decode_connection(self, socket):
        code, data = self._read_packet(socket)

        if code == ConnectSuccess.code:
            message = ConnectSuccess(data)
        elif code in self.message_dict:
            message = self.message_dict[code](data)
        else:
            return self.UnknownMessageClass(code, data)

        obex_version, flags, max_packet_length = struct.unpack(">BBH", data[3:7])

        message.obex_version = OBEX_Version()
        message.obex_version.from_byte(obex_version)
        message.flags = flags
        message.max_packet_length = max_packet_length
        message.read_data(data)
        return message

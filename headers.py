
import struct
import sys

class Header:
    def __init__(self, data, encoded=False):
        if encoded:
            self.data = data
        else:
            self.data = self.encode(data)

class UnicodeHeader(Header):
    def decode(self):
        if sys.version_info.major < 3:
            return unicode(self.data, encoding = "utf_16_be")
        else:
            return str(self.data, encoding = "utf_16_be")

    def encode(self, data):
        encoded_data = data.encode("utf_16_be") + b"\x00\x00"
        return struct.pack(">BH", self.code, len(encoded_data) + 3) + encoded_data

class DataHeader(Header):
    def decode(self):
        return self.data

    def encode(self, data):
        return struct.pack(">BH", self.code, len(data) + 3) + data

class ByteHeader(Header):
    def decode(self):
        return struct.unpack(">B", self.data)[0]

    def encode(self, data):
        return struct.pack(">BB", self.code, data)

class FourByteHeader(Header):
    def decode(self):
        return struct.unpack(">I", self.data)[0]

    def encode(self, data):
        return struct.pack(">BI", self.code, data)

class Count(FourByteHeader):
    code = 0xC0

class Name(UnicodeHeader):
    code = 0x01

class Type(DataHeader):
    code = 0x42

    def encode(self, data):
        if data[-1:] != b"\x00":
            data += b"\x00"
        return struct.pack(">BH", self.code, len(data) + 3) + data

class Length(FourByteHeader):
    code = 0xC3

class Time(DataHeader):
    code = 0x44

class Description(UnicodeHeader):
    code = 0x05

class Target(DataHeader):
    code = 0x46

class HTTP(DataHeader):
    code = 0x47

class Body(DataHeader):
    code = 0x48

class End_Of_Body(DataHeader):
    code = 0x49

class Who(DataHeader):
    code = 0x4A

class Connection_ID(FourByteHeader):
    code = 0xCB

class App_Parameters(DataHeader):
    code = 0x4C

class Auth_Challenge(DataHeader):
    code = 0x4D

class Auth_Response(DataHeader):
    code = 0x4E

class Object_Class(DataHeader):
    code = 0x51

header_dict = {
        0xC0: Count,
        0x01: Name,
        0x42: Type,
        0xC3: Length,
        0x44: Time,
        0x05: Description,
        0x46: Target,
        0x47: HTTP,
        0x48: Body,
        0x49: End_Of_Body,
        0x4A: Who,
        0xCB: Connection_ID,
        0x4C: App_Parameters,
        0x4D: Auth_Challenge,
        0x4E: Auth_Response,
        0x51: Object_Class
}

def header_class(ID):
    try:
        return header_dict[ID]
    except KeyError:
        if 0x30 <= (ID & 0x3f) <= 0x3f:
            return UserDefined

    return Header

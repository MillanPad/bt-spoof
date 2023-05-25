

import sys
from nOBEX.common import OBEX_Version, OBEXError
from nOBEX.bluez_helper import BluetoothSocket
from nOBEX import headers
from nOBEX import requests
from nOBEX import responses
from nOBEX.xml_helper import parse_xml

class Client(object):

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.max_packet_length = 0xffff
        self.obex_version = OBEX_Version()
        self.response_handler = responses.ResponseHandler()

        self.socket = None
        self._external_socket = False
        self.connection_id = None

    def _send_headers(self, request, header_list, max_length):
        

        if self.connection_id:
            header_list.insert(0, self.connection_id)

        while header_list:
            if request.add_header(header_list[0], max_length):
                header_list.pop(0)
            else:
                self.socket.sendall(request.encode())

                if isinstance(request, requests.Connect):
                    response = self.response_handler.decode_connection(self.socket)
                else:
                    response = self.response_handler.decode(self.socket)

                if not isinstance(response, responses.Continue):
                    return response

                request.reset_headers()

 
        if isinstance(request, requests.Get):
           
            request.code = requests.Get_Final.code

        self.socket.sendall(request.encode())

        if isinstance(request, requests.Connect):
            response = self.response_handler.decode_connection(self.socket)
        else:
            response = self.response_handler.decode(self.socket)

        return response

    def _collect_parts(self, header_list):
        body = []
        new_headers = []
        for header in header_list:
            if isinstance(header, headers.Body):
                body.append(header.data)
            elif isinstance(header, headers.End_Of_Body):
                body.append(header.data)
            else:
                new_headers.append(header)

        return new_headers, b"".join(body)

    def set_socket(self, socket):

        self.socket = socket

        if socket is None:
            self._external_socket = False
        else:
            self._external_socket = True

    def connect(self, header_list = ()):

        if not self._external_socket:
            self.socket = BluetoothSocket()

        self.socket.connect((self.address, self.port))

        flags = 0
        data = (self.obex_version.to_byte(), flags, self.max_packet_length)

        max_length = self.max_packet_length
        request = requests.Connect(data)

        header_list = list(header_list)
        response = self._send_headers(request, header_list, max_length)

        if isinstance(response, responses.ConnectSuccess):
            self.remote_info = response
            for header in response.header_data:
                if isinstance(header, headers.Connection_ID):
                    self.connection_id = headers.Connection_ID(header.decode())
        elif not self._external_socket:
            self.socket.close()

        if not isinstance(response, responses.ConnectSuccess):
            raise OBEXError(response)

    def disconnect(self, header_list = ()):
        max_length = self.remote_info.max_packet_length
        request = requests.Disconnect()

        header_list = list(header_list)
        response = self._send_headers(request, header_list, max_length)

        if not self._external_socket:
            self.socket.close()

        self.connection_id = None

        if not isinstance(response, responses.Success):
            raise OBEXError(response)

    def put(self, name, file_data, header_list = ()):
        for response in self._put(name, file_data, header_list):
            if isinstance(response, responses.Continue) or \
                    isinstance(response, responses.Success):
                continue
            else:
                raise OBEXError(response)

    def _put(self, name, file_data, header_list = ()):
        header_list = [
                headers.Name(name),
                headers.Length(len(file_data))
                ] + list(header_list)

        max_length = self.remote_info.max_packet_length
        request = requests.Put()

        response = self._send_headers(request, header_list, max_length)
        yield response

        if not isinstance(response, responses.Continue):
            return

        optimum_size = max_length - 3 - 3

        i = 0
        while i < len(file_data):
            data = file_data[i:i+optimum_size]
            i += len(data)
            if i < len(file_data):
                request = requests.Put()
                request.add_header(headers.Body(data, False), max_length)
                self.socket.sendall(request.encode())

                response = self.response_handler.decode(self.socket)
                yield response

                if not isinstance(response, responses.Continue):
                    return

            else:
                request = requests.Put_Final()
                request.add_header(headers.End_Of_Body(data, False), max_length)
                self.socket.sendall(request.encode())

                response = self.response_handler.decode(self.socket)
                yield response

                if not isinstance(response, responses.Success):
                    return

    def get(self, name = None, header_list = ()):
        returned_headers = []

        for response in self._get(name, header_list):
            if isinstance(response, responses.Continue) or \
                    isinstance(response, responses.Success):
                
                returned_headers += response.header_data
            else:
              
                raise OBEXError(response)

        return self._collect_parts(returned_headers)

    def _get(self, name = None, header_list = ()):
        header_list = list(header_list)
        if name is not None:
            header_list = [headers.Name(name)] + header_list

        max_length = self.remote_info.max_packet_length
        request = requests.Get()

        response = self._send_headers(request, header_list, max_length)
        yield response

        if not (isinstance(response, responses.Continue) or
                isinstance(response, responses.Success)):
            return

        file_data = []
        request = requests.Get_Final()

        while isinstance(response, responses.Continue):
            self.socket.sendall(request.encode())
            response = self.response_handler.decode(self.socket)
            yield response

    def setpath(self, name = "", create_dir = False, to_parent = False, header_list = ()):
        header_list = list(header_list)
        if name is not None:
            header_list = [headers.Name(name)] + header_list

        max_length = self.remote_info.max_packet_length

        flags = 0
        if not create_dir:
            flags |= requests.Set_Path.DontCreateDir
        if to_parent:
            flags |= requests.Set_Path.NavigateToParent

        request = requests.Set_Path((flags, 0))

        response = self._send_headers(request, header_list, max_length)

        if not isinstance(response, responses.Success):
            raise OBEXError(response)

    def delete(self, name, header_list = ()):

        header_list = [
                headers.Name(name)
                ] + list(header_list)

        max_length = self.remote_info.max_packet_length
        request = requests.Put_Final()

        response = self._send_headers(request, header_list, max_length)

        if not isinstance(response, responses.Success):
            raise OBEXError(response)

    def abort(self, header_list = ()):

        header_list = list(header_list)
        max_length = self.remote_info.max_packet_length
        request = requests.Abort()

        response = self._send_headers(request, header_list, max_length)

        if not isinstance(response, responses.Success):
            raise OBEXError(response)

    def listdir(self, name = "", xml=False):

        hdrs, data = self.get(name,
                header_list=[headers.Type(b"x-obex/folder-listing", False)])

        if xml:
            return data

        tree = parse_xml(data)
        folders = []
        files = []
        for e in tree:
            if e.tag == "folder":
                folders.append(e.attrib["name"])
            elif e.tag == "file":
                files.append(e.attrib["name"])
            elif e.tag == "parent-folder":
                pass # ignore it
            else:
                sys.stderr.write("Unknown listing element %s\n" % e.tag)

        return folders, files

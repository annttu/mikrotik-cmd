#!/usr/bin/env python3
# encoding: utf-8

import logging
import socket
import struct
from hashlib import md5
import binascii


logger = logging.getLogger("MikrotikAPI")


class MikrotikAPIError(Exception):
    pass


def pack_length(length):
    """
    Pack api request length.
    http://wiki.mikrotik.com/wiki/Manual:API#Protocol
    """
    if length < 0x80:
        return struct.pack("!B", length)
    elif length <= 0x3FFF:
        length = length | 0x8000
        return struct.pack("!BB", (length >> 8) & 0xFF, length & 0xFF)
    elif length <= 0x1FFFFF:
        length = length | 0xC00000
        return struct.pack("!BBB", length >> 16, (length & 0xFFFF) >> 8, length & 0xFF)
    elif length <= 0xFFFFFFF:
        length = length | 0xE0000000
        return struct.pack("!BBBB", length >> 24, (length & 0xFFFFFF) >> 16, (length & 0xFFFF) >> 8, length & 0xFF)
    else:
        raise MikrotikAPIError("Too long command!")


def unpack_length(length):
    """
    Unpack api request length.
    :param length: length string to unpack
    :return: length as integer
    """
    if len(length) == 1:
        return struct.unpack("!B", length)[0]
    elif len(length) == 2:
        (a, b) =  struct.unpack("!BB", length)
        return a << 8 + b
    elif len(length) == 3:
        (a,b,c) = struct.unpack("!BBB", length)
        return a << 16 + b << 8 + c
    elif len(length) == 4:
        (a,b,c,d) = struct.unpack("!BBBB", length)
        return (a << 24) + (b << 16) + (c << 8) + d
    raise MikrotikAPIError("Invalid message length %s!" % length)

class ResponseTypes:
    STATUS = 1
    ERROR = 2
    DATA = 3


class MikrotikApiResponse(object):
    def __init__(self, status, type, attributes=None, error=None):
        self.status = status
        self.type = type
        self.attributes = attributes
        self.error = error


class MikrotikAPIRequest(object):
    def __init__(self, command, attributes=None, api_attributes=None, queries=None):
        """
        Generate request for Mikrotik RouterOS API.
        """
        if not command.startswith('/'):
            raise MikrotikAPIError("Command should start with /")
        self.command = command
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        if api_attributes:
            self.api_attributes = api_attributes
        else:
            self.api_attributes = {}
        if queries:
            self.queries = queries
        else:
            self.queries = {}

    def get_request(self):
        request = []


        request.append(pack_length(len(self.command)))
        request.append(self.command.encode("utf-8"))

        for attribute, value in self.attributes.items():
            attrib = "=%s=%s" % (attribute, value)
            request.append(pack_length(len(attrib)))
            request.append(attrib.encode("utf-8"))

        for attribute, value in self.api_attributes.items():
            attrib = ".%s=%s" % (attribute, value)
            request.append(pack_length(len(attrib)))
            request.append(attrib.encode("utf-8"))

        # TODO: complete query parsing
        for key, value in self.queries:
            if value:
                query = "?%s=%s" % (key, value)
            else:
                query = "?%s" % (key,)
            request.append(pack_length(len(query)))
            request.append(query.encode("utf-8"))

        request.append(pack_length(0))
        return b''.join(request)


class Mikrotik(object):
    def __init__(self, address, port=8728):
        self._address = address
        self._port = port
        self.connect()

    def connect(self):
        self._socket = socket.socket()
        self._socket.connect((self._address, self._port))

    def _send(self, data):
        print("Sending %s" % data.decode("utf-8"))
        self._socket.send(data)

    def _recv(self):
        # TODO: DO magic!!
        responses = self._socket.recv(16384)
        if len(responses) < 2:
            raise MikrotikAPIError("Invalid response from API: too short message")
        if responses[-1] != 0:
            raise MikrotikAPIError("Invalid response from API: message is not complete")
        return_values = []
        for response in responses.split(b'\x00')[:-1]:
            f = response.decode("utf-8").find("!")
            length = unpack_length(response[:f])
            response = response[f:]
            status = response[1:length]
            if status not in [b'done', b'trap', b'fatal', b're']:
                raise MikrotikAPIError("Invalid response from API: invalid status %s" % status)
            if status == b'done':
                logger.debug("Got %s from api" % response[length+1:])
                return_values.append(response[length+1:])
            elif status == b'trap':
                raise MikrotikAPIError("Got error from API: %s" % response[length+1:])
            else:
                raise MikrotikAPIError("Got unknown error from API: %s" % response[length+1:])
        return return_values

    def login(self, username, password):
        r = MikrotikAPIRequest(command="/login")
        self._send(r.get_request())
        response = self._recv()[0].decode("utf-8")
        (key, value) = response[1:].split('=', 1)
        print(len(value))
        value = binascii.unhexlify(value.strip())
        if key == 'ret':
            md = md5()
            md.update('\x00'.encode("utf-8"))
            md.update(password.encode("utf-8"))
            md.update(value)
            r = MikrotikAPIRequest(command="/login", attributes={'name': username, 'response': "00" + md.hexdigest()})
            self._send(r.get_request())
        raise MikrotikAPIError("Cannot log in!")

    def disconnect(self):
        self._socket.shutdown()
        self._socket.close()

if __name__ == '__main__':
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    m = Mikrotik('10.0.0.1')
    m.login('admin','admin')


#!/usr/bin/env python3

import message
import struct

from socket import *
from socketserver import BaseRequestHandler, UDPServer

class ChatUDPHandler(BaseRequestHandler):
  def handle(self):
    # Retrieve the data and the socket.
    data, socket = (self.request[0].strip(), self.request[1])

    # Unpack the message.
    msg = message.deserialize(data)
    print('{} ({}): {}'.format(msg.name, msg.team, msg.text))
    #socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
  server = UDPServer(("", 59595), ChatUDPHandler)
  server.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  mreq = struct.pack("=4sl", inet_aton("224.1.1.1"), INADDR_ANY)
  server.socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
  server.serve_forever()


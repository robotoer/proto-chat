#!/usr/bin/env python3

import struct
from socket import *
from socketserver import BaseRequestHandler, UDPServer
import header

class ChatUDPHandler(BaseRequestHandler):
  def handle(self):
    data = self.request[0].strip()
    socket = self.request[1]

    msg = header.Message(data)
    print("{} wrote:".format("anon" if msg.anon else msg.source))
    print(msg.line)
    socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
  server = UDPServer(("", 59595), ChatUDPHandler)
  server.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  mreq = struct.pack("=4sl", inet_aton("224.1.1.1"), INADDR_ANY)
  server.socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
  server.serve_forever()


#!/usr/bin/env python3

import argparse
import message
import struct

from constants import GROUP
from socket import *
from socketserver import BaseRequestHandler, UDPServer

logfile = open('chat.log', 'a')
class ChatUDPHandler(BaseRequestHandler):
  def handle(self):
    # Retrieve the data and the socket.
    data, socket = (self.request[0].strip(), self.request[1])

    # Unpack the message.
    msg = message.deserialize(data)
    logfile.write('{} ({}): {}\n'.format(msg.name, msg.team, msg.text))

    if msg.text == 'logclose':
      logfile.close()
      print('logfile closed')

if __name__ == "__main__":
  # Get command line arguments.
  parser = argparse.ArgumentParser()
  parser.add_argument('port', type=int, help='The multicast port to listen on.')
  args = parser.parse_args()

  # Setup the socket
  server = UDPServer((GROUP, args.port), ChatUDPHandler)
  server.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  mreq = struct.pack("=4sl", inet_aton(GROUP), INADDR_ANY)
  server.socket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

  # Start the server
  server.serve_forever()


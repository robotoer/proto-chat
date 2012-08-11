#!/usr/bin/env python3

import argparse
import re
import socket
import threading

from message import serialize, deserialize

class ResponseHandler:
  def __init__(self, sock):
    self.sock = sock
    self.stop = False

  def serve_forever(self):
    while not self.stop:
      name, team, dest, data = deserialize(self.sock.recv(1024))
      print('{} ({}) -> {}: {}'.format(name, team, dest, data))

def game_server_socket(address):
  # Match the address string with a regular expression.
  matched = re.match('^(\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?):(\d+)$', address)
  if not matched:
    raise argparse.ArgumentTypeError('This is not a valid game server address')

  # Get the ip address & port from the regular expression match.
  ip   = matched.group(1)
  port = int(matched.group(2))

  return socket.create_connection((ip, port))

if __name__ == "__main__":
  # Get command line arguments.
  parser = argparse.ArgumentParser()
  parser.add_argument('server', type=game_server_socket, help='The ip address and port of the game server')
  parser.add_argument('team', choices=['russians', 'americans'], help='The allegiance of the player')
  parser.add_argument('name', help='The player name to use')
  args = parser.parse_args()

  # Get parameters.
  sock   = args.server
  team   = args.team
  name   = args.name
  # TODO: This should use $PS2
  prompt = 'all > '
  dest   = 'all'

  # Start listening for responses from the server.
  response_handler = ResponseHandler(sock)
  response_thread = threading.Thread(target=response_handler.serve_forever)
  response_thread.daemon = True
  response_thread.start()

  # Try-block to ensure socket gets closed even if something goes wrong.
  try:
    # Send client information to the server.
    sock.sendall(serialize(name, team, name, '/open'))

    # Get the first line of input.
    line = input(prompt)
    while line != '/quit':
      # Catch any command messages.
      if line.startswith('/'):
        if re.match('/channel (.*)', line):
          dest = re.match('/channel (.*)', line).group(1)
          prompt = '{} > '.format(dest)
        else:
          # Unknown command.
          print('Unknown command: {}'.format(line))

      # Send a message.
      else:
        # Send the message
        sock.sendall(serialize(name, team, dest, line))

      # Get the next line of input.
      line = input(prompt)
  finally:
    sock.sendall(serialize(name, team, name, '/close'))
    sock.close()

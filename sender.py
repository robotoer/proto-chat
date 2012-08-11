#!/usr/bin/env python3

from chatlogging import get
from message import serialize, deserialize
import argparse
import re
import socket
import threading

logger = get('client')

class ResponseHandler:
  def __init__(self, sock):
    self.sock   = sock
    self.stop   = False
    self.drop   = None
    self.jammed = False

  def serve_forever(self):
    while not self.stop:
      name, team, dest, data = deserialize(self.sock.recv(1024))
      if data == '/drop' and self.drop != None:
        sock.sendall(self.drop)
        self.drop = None

      if self.jammed:
        logger.info('jammed -> {}: {}'.format(dest, data))
      else:
        logger.info('{} ({}) -> {}: {}'.format(name, team, dest, data))

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
        if re.match('/channel (.+)', line):
          dest = re.match('/channel (.+)', line).group(1)
          prompt = '{} > '.format(dest)

        elif re.match('/drop (.+)', line):
          drop_message = re.match('/drop (.+)', line).group(1)
          response_handler.drop = serialize(name, team, dest, '/drop {}'.format(drop_message))

        elif re.match('/effect (.+) (.*)', line):
          matched = re.match('/effect (.+) (.*)', line)
          effect = matched.group(1)
          if effect == 'jamming':
            response_handler.jammed = matched.group(2) == 'on'
          else:
            logger.warning('Unknown effect: {}'.format(effect))

        elif re.match('/use wiretapping (.+)', line):
          target = re.match('/use wiretapping (.+)', line).group(1)
          logger.info('Wiretapping {}'.format(target))
          sock.sendall(serialize(name, team, name, '/wiretap {}'.format(target)))

        else:
          # Unknown command.
          logger.warning('Unknown command: {}'.format(line))

      # Send a message.
      else:
        # Send the message
        sock.sendall(serialize(name, team, dest, line))

      # Get the next line of input.
      line = input(prompt)
  finally:
    sock.sendall(serialize(name, team, name, '/close'))
    sock.close()

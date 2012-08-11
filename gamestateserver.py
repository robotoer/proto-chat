#!/usr/bin/env python3

from chatlogging import get
from message import serialize, deserialize
import re
import socket
import socketserver
import threading

logger = get('server')

class ClientConnection(socketserver.StreamRequestHandler):
  def setup(self):
    socketserver.StreamRequestHandler.setup(self)

    # Wait for the /open message.
    name, team, dest, data = deserialize(self.rfile.readline())
    if data != '/open':
      raise ValueError('First message ({}) to game server was not a /open'.format(data))

    # Add the client to the appropriate groups.
    self.server.connections[self.client_address] = self.wfile
    self.server.names[name] = self.client_address
    self.server.names[self.client_address] = name
    if team == 'russians':
      self.server.russians.add(self.client_address)
    elif team == 'americans':
      self.server.americans.add(self.client_address)
    else:
      raise ValueError('Invalid team: {}'.format(team))

    logger.info('{} ({}) connected to: {}'.format(name, team, self.client_address))

  def handle(self):
    message = self.rfile.readline()
    name, team, dest, data = deserialize(message)
    while data != '/close':
      # Handle wiretap enabling.
      if re.match('/wiretap (.+)', data):
        target = re.match('/wiretap (.+)', data).group(1)
        logger.info('{} now wiretapping {}'.format(name, target))
        if target in self.server.wiretaps:
          self.server.wiretaps[target].append(name)
        else:
          self.server.wiretaps[target] = [name]

      # Redirect wiretapped messages. This can be easily moved into the private message block below.
      if name in self.server.wiretaps:
        targets = [self.server.names[x] for x in self.server.wiretaps[name]]
        self.server.send_to_group(message, set(targets))
        del self.server.wiretaps[name]

      logger.info('{} ({}) -> {}: {}'.format(name, team, dest, data))

      # Resend packet.
      if dest == 'all':
        self.server.send_to_group(message, self.server.russians.union(self.server.americans))
      elif dest == 'russians':
        self.server.send_to_group(message, self.server.russians)
      elif dest == 'americans':
        self.server.send_to_group(message, self.server.americans)
      elif dest in self.server.names:
        self.server.send_to_group(message, set([self.server.names[dest]]))
      else:
        raise ValueError('Invalid dest: {}'.format(dest))

      # Get the next message.
      message = self.rfile.readline()
      name, team, dest, data = deserialize(message)

  def finish(self):
    connections = self.server.connections
    americans = self.server.americans
    russians = self.server.russians
    names = self.server.names
    client_address = self.client_address

    name = names[client_address]

    del connections[client_address]
    del names[client_address]
    del names[name]
    if client_address in americans:
      americans.remove(client_address)
    if client_address in russians:
      russians.remove(client_address)

    logger.info('{} closing connection: {}'.format(name, client_address))

class GameServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  def server_activate(self):
    # Initialize chat groups.
    self.connections = {}
    self.americans = set()
    self.russians = set()
    # This is a bi-map.
    self.names = {}

    # Stuff for abilities etc.
    self.jammed = False
    self.wiretaps = {}

    # Start the server.
    logger.info('starting game server at {}'.format(self.server_address))
    socketserver.TCPServer.server_activate(self)

  def send_to_group(self, message, group):
    for client in group:
      client_wfile = self.connections[client]
      client_wfile.write(message)

def game_server(address):
  matched = re.match('^(\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?):(\d+)$', address)
  if not matched:
    raise argparse.ArgumentTypeError('This is not a valid game server address')

if __name__ == "__main__":
  # Start a thread with the server -- that thread will then start one more thread for each request.
  server = GameServer(('localhost', 59595), ClientConnection)
  ip, port = server.server_address
  server_thread = threading.Thread(target=server.serve_forever)

  # Exit the server thread when the main thread terminates
  server_thread.daemon = True
  server_thread.start()

  # Get the first line of input.
  prompt = '{}:{} > '.format(ip, port)
  line = input(prompt)
  while line != 'quit':
    # Print currently connected clients.
    if line == 'clients':
      logger.info(server.connections)

    # Print current wiretaps.
    elif line == 'wiretaps':
      logger.info(server.wiretaps)

    # Send dead drop.
    elif line == 'drop':
      logger.info('Sending any dead drops.')
      server.send_to_group(serialize('server', 'server', 'all', '/drop'), server.russians.union(server.americans))

    # Radio jamming.
    elif line == 'radiojamming':
      logger.info('Radio Jamming used.')

    # Unknown command.
    else:
      logger.info('Unknown command: {}'.format(line))

    # Get the next line of input.
    line = input(prompt)

  # Cleanup once we're done.
  server.shutdown()

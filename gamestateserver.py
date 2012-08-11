#!/usr/bin/env python3

from message import serialize, deserialize
import socket
import socketserver
import threading

class ClientConnection(socketserver.StreamRequestHandler):
  def send_to_group(self, message, group):
    for client in group:
      client_wfile = self.server.connections[client]
      client_wfile.write(message)

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
    # add support for private messages.
    else:
      raise ValueError('Invalid team: {}'.format(team))

    print('connected to: {}'.format(self.client_address))

  def handle(self):
    message = self.rfile.readline()
    name, team, dest, data = deserialize(message)
    while data != '/close':
      print('{} ({}) -> {}: {}'.format(name, team, dest, data))

      # Resend packet.
      if dest == 'all':
        self.send_to_group(message, self.server.russians.union(self.server.americans))
      elif dest == 'russians':
        self.send_to_group(message, self.server.russians)
      elif dest == 'americans':
        self.send_to_group(message, self.server.americans)
      elif dest in self.server.names:
        self.send_to_group(message, set([self.server.names[dest]]))
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

    print('closing connection: {}'.format(client_address))

class GameServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  def server_activate(self):
    # Initialize chat groups.
    self.connections = {}
    self.americans = set()
    self.russians = set()
    # This is a bi-map.
    self.names = {}

    # Start the server.
    print('starting game server at {}'.format(self.server_address))
    socketserver.TCPServer.server_activate(self)

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
  print("Server loop running in thread:", server_thread.name)

  # Get the first line of input.
  prompt = '{}:{} > '.format(ip, port)
  line = input(prompt)
  while line != 'quit':
    # Print currently connected clients.
    if line == 'clients':
      print(server.connections)
    # Unknown command.
    else:
      print('Unknown command: {}'.format(line))

    # Get the next line of input.
    line = input(prompt)

  # Cleanup once we're done.
  server.shutdown()

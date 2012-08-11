#!/usr/bin/env python3

from message import serialize, deserialize
import socket
import socketserver
import threading

class ClientConnection(socketserver.StreamRequestHandler):
  def __init__(self, request, client_address, server):
    server.connections.append(client_address)
    socketserver.StreamRequestHandler.__init__(self, request, client_address, server)

  def handle(self):
    name, team, data = deserialize(self.rfile.readline())
    cur_thread = threading.current_thread()
    response = serialize(name, team, "{}: {}".format(cur_thread.name, data))
    self.wfile.write(response)

class GameServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  def __init__(self, server_address, handler_class=ClientConnection):
    self.connections = []
    socketserver.TCPServer.__init__(self, server_address, handler_class)

def client(ip, port, message):
  # Connect to the server.
  sock = socket.create_connection((ip, port))

  try:
    sock.sendall(serialize('name', 'r', message))
    name, team, response = deserialize(sock.recv(1024))
    print("{} ({}): {}".format(name, team, response))
  finally:
    sock.close()

if __name__ == "__main__":
  # Port 0 means to select an arbitrary unused port
  HOST, PORT = "localhost", 0

  server = GameServer((HOST, PORT))
  ip, port = server.server_address

  # Start a thread with the server -- that thread will then start one
  # more thread for each request
  server_thread = threading.Thread(target=server.serve_forever)
  # Exit the server thread when the main thread terminates
  server_thread.daemon = True
  server_thread.start()
  print("Server loop running in thread:", server_thread.name)

  client(ip, port, "Hello World 1")
  client(ip, port, "Hello World 2")
  client(ip, port, "Hello World 3")

  print(server.connections)

  server.shutdown()

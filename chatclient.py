#!/usr/bin/env python3

import argparse
import re

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP, IPPROTO_IP, IP_MULTICAST_TTL
from message import *
from constants import ALL, AMERICANS, RUSSIANS, GROUP

# Get command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument('team', choices=['russian', 'american'], help='The allegiance of the player')
parser.add_argument('name', help='The player name to use')
args = parser.parse_args()

# Create a multicast UDP socket.
sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 2)

# Set the program defaults.
audience  = ALL
team      = { 'russian': 'r', 'american': 'a' }[args.team]
name      = args.name
group     = GROUP
prompt    = 'All > '

# Get the first line of input.
line = input(prompt)
while line != '/quit':
  # Catch any command messages.
  if line.startswith('/'):
    # Switch to allchat
    if re.match('^/all$', line):
      audience = ALL
      prompt = 'All > '

    # Switch to american teamchat.
    elif re.match('^/ateam$', line):
      audience = AMERICANS
      prompt = 'AMERICANS > '

    # Switch to russian teamchat.
    elif re.match('^/rteam$', line):
      audience = RUSSIANS
      prompt = 'RUSSIANS > '

    # Unknown command.
    else:
      print('Unknown command: {}'.format(line))

  else:
    # Build a message object.
    message = Message(name, team, line)

    # Send the message
    sock.sendto(serialize(message), (group, audience))

  # Get the next line of input.
  line = input(prompt)

sock.close()


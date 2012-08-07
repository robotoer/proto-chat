#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP, IPPROTO_IP, IP_MULTICAST_TTL
import header

sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 2)

line = input("All > ")
while line != "/quit":
  sock.sendto(header.head(bytes("me", "utf-8"), bytes("you", "utf-8"), False, True, bytes((line), "utf-8")), ("224.1.1.1", 59595))
  line = input("All > ")

sock.close()


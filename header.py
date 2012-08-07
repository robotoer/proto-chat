#!/usr/bin/env python3

import struct

format_string = "4s4s??4s"

def serialize(source, channel, anon, fakeable, line):
        return struct.pack(format_string, source, channel, anon, fakeable, line)
    
def deserialize(packed):
        return struct.unpack(format_string, packed)

class Message:
    def __init__(self, packed):
        self.source, self.channel, self.anon, self.fakeable, self.line = deserialize(packed)
        self.source = self.source.decode("utf-8")
        self.channel = self.channel.decode("utf-8")
        self.line = self.line.decode("utf-8")

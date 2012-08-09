from struct import pack, unpack, calcsize

# Header Format:
#
#          [        Header        ][ Message  ]
#   type:   ( string[10] )( byte )..( string )
#   header: [    name    ][ team ]..[  text  ]
#
# see http://docs.python.org/py3k/library/struct.html#format-characters for a full
# listing of format string identifiers.
HEADER_FORMAT    = "!10sb"
HEADER_SIZE      = calcsize(HEADER_FORMAT)
MESSAGE_ENCODING = 'utf-8'

def serialize(message):
  # Build the header.
  header = pack(HEADER_FORMAT, message.name.ljust(10).encode(MESSAGE_ENCODING), ord(message.team))

  # Encode the message text.
  text = message.text.encode(MESSAGE_ENCODING)

  return header + text

def deserialize(packed):
  # Split the header from the message
  header, text = (packed[:HEADER_SIZE], packed[HEADER_SIZE:].decode(MESSAGE_ENCODING))

  # Serialize the data using the struct library.
  # See http://docs.python.org/py3k/library/struct.html#struct.pack.
  name, team = unpack(HEADER_FORMAT, header)

  # Build a Message object and return it.
  return Message(name.decode(MESSAGE_ENCODING).strip(), chr(team), text)

class Message:
  def __init__(self, name, team, text):
    self.name = name
    self.team = team
    self.text = text

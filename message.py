import json

ENCODING = 'utf-8'

def serialize(name, team, dest, text):
  # Build message as a json dictionary.
  jsonified = json.dumps({'name': name, 'team': team, 'dest': dest, 'text': text})

  # Add a newline character to mark the end of the message.
  return bytes(jsonified + '\n', ENCODING)

def deserialize(data):
  # Deserialize json into a dictionary.
  dictionary = json.loads(str(data, ENCODING))

  # Build a message tuple and return it.
  return (dictionary['name'], dictionary['team'], dictionary['dest'], dictionary['text'])

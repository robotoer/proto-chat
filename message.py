import json

ENCODING = 'utf-8'

def serialize(name, team, text):
  # Build message as a json dictionary.
  jsonified = json.dumps({'name': name, 'team': team, 'text': text})

  # Add a newline character to mark the end of the message.
  return bytes(jsonified + '\n', ENCODING)

def deserialize(data):
  # Deserialize json into a dictionary.
  dictionary = json.loads(str(data, ENCODING))

  # Build a message tuple and return it.
  return (dictionary['name'], dictionary['team'], dictionary['text'])

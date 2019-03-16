import json
from collections import deque
from enum import EnumMeta

class Event(EnumMeta):
  MY_ADDRESS = 'MY_ADDRESS'
  GET_PEERS_REQUEST = 'GET_PEERS_REQUEST'
  GET_PEERS_RESPONSE = 'GET_PEERS_RESPONSE'
  ADD_TRANSACTION = 'ADD_TRANSACTION'

  @staticmethod
  def construct(event_type, data=None):
    event = { 'event': event_type }
    if data:
      event['data'] = data

    return json.dumps(event)

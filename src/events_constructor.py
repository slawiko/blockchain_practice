import json
from collections import deque
from enum import EnumMeta

class EventsQueue():
  def __init__(self, iterable=[]):
    self.queue = deque(iterable)

  def get(self):
    return self.queue.popleft()

  def put(self, element):
    self.queue.append(element)

class Event(EnumMeta):
  MY_ADDRESS = 'MY_ADDRESS'
  GET_PEERS_REQUEST = 'GET_PEERS_REQUEST'
  GET_PEERS_RESPONSE = 'GET_PEERS_RESPONSE'

  @staticmethod
  def construct(event_type, data=None):
    event = { 'event': event_type }
    if data:
      event['data'] = data

    return json.dumps(event)

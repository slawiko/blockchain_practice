import json
from collections import deque

class EventsQueue():
  def __init__(self, iterable=[]):
    self.queue = deque(iterable)

  def get(self):
    return self.queue.popleft()

  def put(self, element):
    self.queue.append(element)

def event_my_address_response(address):
  return json.dumps({ 'event': 'MY_ADDRESS_RESPONSE', 'data': address })

def event_get_peers_request():
  return json.dumps({ 'event': 'GET_PEERS_REQUEST' })

def event_get_peers_response(data):
  return json.dumps({ 'event': 'GET_PEERS_RESPONSE', 'data': data })

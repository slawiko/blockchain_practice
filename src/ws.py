import json
import asyncio

import websockets
from websockets.exceptions import ConnectionClosed

from pool import Pool
from events_constructor import Event

class Node():
  def __init__(self, seeds=[('127.0.0.1', 8765)], port=80):
    self.seeds = seeds
    self.address = ('127.0.0.1', int(port))
    self.pool = Pool()
  
  async def start(self):
    await websockets.serve(self.listen_incoming, self.address[0], self.address[1])
    print(f'ws server started at {self.address[0]}:{self.address[1]}')
    await self.connect(self.seeds)
    print(f'ws server connected to peers')
    await self.schedule_task()
    print(f'ws scheduled task')
  
  async def connect(self, addresses):
    for address in addresses:
      websocket = await websockets.connect(f'ws://{address[0]}:{address[1]}')
      await self.listen_outgoing(websocket, address)

  async def broadcast_event(self, event):
    tasks = [Node.send(connection, event) for connection in self.pool.connections]
    if len(tasks) > 0:
      print(f'broadcast on {len(tasks)} peers')
      await asyncio.gather(*tasks)
    else:
      print(f'no one to broadcast')

  async def schedule_task(self):
    async def get_new_peers():
      event = Event.construct(Event.GET_PEERS_REQUEST)
      while True:
        await asyncio.sleep(15)
        await self.broadcast_event(event)
    try:
      asyncio.get_event_loop().create_task(get_new_peers())
    except Exception as error:
      print(f'unable to connect. {error}')

  async def listen(self, websocket, uri=''):
    while True:
      message = await websocket.recv()
      print(f'Received {message} from {websocket.local_address}:{websocket.remote_address}')
      answer = await self.handle_message(message, websocket)
      if answer:
        await Node.send(websocket, answer)
        print(f'Sent {answer} to {websocket.local_address}')

  async def listen_outgoing(self, websocket, address):
    await self.pool.register_connection(address, websocket, 'to')
    asyncio.ensure_future(self.listen(websocket))
    my_address_event = Event.construct(Event.MY_ADDRESS, self.address)
    await Node.send(websocket, my_address_event)

  async def listen_incoming(self, websocket, uri=''):
    # TODO: why await? It doesn't work without await
    asyncio.ensure_future(await self.listen(websocket, uri))

  def handle_get_peers_request(self):
    return Event.construct(Event.GET_PEERS_RESPONSE, self.pool.addresses)

  async def handle_get_peers_response(self, addresses):
    new_addresses = [address for address in addresses if address not in self.pool.peers]
    new_addresses.remove(self.address)
    if new_addresses:
      print(f'New peers found: {new_addresses}')
      await self.connect(new_addresses)
    print(f'No new peers found')

  async def handle_message(self, message, websocket):
    event = json.loads(message)
    answer = None
    if event['event'] == Event.GET_PEERS_REQUEST:
      answer = self.handle_get_peers_request()
    elif event['event'] == Event.GET_PEERS_RESPONSE:
      addresses = [tuple(x) for x in event['data']]
      asyncio.ensure_future(self.handle_get_peers_response(addresses))
    elif event['event'] == Event.MY_ADDRESS:
      address = tuple(event['data'])
      await self.pool.register_connection(address, websocket, 'from')
    else:
      print(f'Unknown event {event}')
    return answer

  @staticmethod
  async def send(websocket, message):
    try:
      print(f'Sending {message} to {websocket.local_address}:{websocket.remote_address}')
      await websocket.send(message)
    except ConnectionClosed as error1:
      print(f'Connection to {websocket} is closed. {error1}')
    except Exception as error2:
      print(f'Unexpected error occured during send {error2}')

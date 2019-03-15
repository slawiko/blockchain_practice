import json
import asyncio

import websockets
from websockets.exceptions import ConnectionClosed

from pool import Pool
from event import Event

class Node():
  def __init__(self, seeds, ip='127.0.0.1', port=80, auto_discovering=True, auto_discovering_interval=60):
    self.address = (ip, int(port))
    self._auto_discovering = auto_discovering
    self._auto_discovering_interval = auto_discovering_interval
    self._seeds = seeds
    self._pool = Pool()
  
  async def start(self):
    await websockets.serve(self._listen_incoming, self.address[0], self.address[1])
    print(f'ws server started at {self.address[0]}:{self.address[1]}')
    await self._connect(self._seeds)
    print(f'ws server connected to peers')
    if self._auto_discovering:
      await self._start_auto_discover()
      print(f'auto discovering started')
  
  async def _connect(self, addresses):
    for address in addresses:
      websocket = await websockets.connect(f'ws://{address[0]}:{address[1]}')
      await self._listen_outgoing(websocket, address)

  async def broadcast(self, event):
    tasks = [Node.send(connection, event) for connection in self._pool.connections]
    if len(tasks) > 0:
      print(f'broadcast on {len(tasks)} peers')
      await asyncio.gather(*tasks)
    else:
      print(f'no one to broadcast')

  async def _start_auto_discover(self):
    async def get_new_peers():
      event = Event.construct(Event.GET_PEERS_REQUEST)
      while True:
        await asyncio.sleep(self._auto_discovering_interval)
        await self.broadcast(event)
    try:
      asyncio.get_event_loop().create_task(get_new_peers())
    except Exception as error:
      print(f'unable to connect. {error}')

  async def _listen(self, websocket, uri=''):
    while True:
      message = await websocket.recv()
      print(f'Received {message} from {websocket.local_address}:{websocket.remote_address}')
      answer = await self._handle_message(message, websocket)
      if answer:
        await Node.send(websocket, answer)
        print(f'Sent {answer} to {websocket.local_address}')

  async def _listen_outgoing(self, websocket, address):
    await self._pool.register_connection(address, websocket, 'to')
    asyncio.ensure_future(self._listen(websocket))
    my_address_event = Event.construct(Event.MY_ADDRESS, self.address)
    await Node.send(websocket, my_address_event)

  async def _listen_incoming(self, websocket, uri=''):
    # TODO: why await? It doesn't work without await
    asyncio.ensure_future(await self._listen(websocket, uri))

  def _handle_get_peers_request(self):
    return Event.construct(Event.GET_PEERS_RESPONSE, self._pool.addresses)

  async def _handle_get_peers_response(self, data):
    addresses = [tuple(x) for x in data]
    new_addresses = [address for address in addresses if address not in self._pool.peers]
    new_addresses.remove(self.address)
    if new_addresses:
      print(f'New peers found: {new_addresses}')
      await self._connect(new_addresses)
    print(f'No new peers found')

  async def _handle_my_address(self, data, websocket):
    address = tuple()
    await self._pool.register_connection(address, websocket, 'from')

  async def _handle_message(self, message, websocket):
    event = json.loads(message)
    answer = None
    if event['event'] == Event.GET_PEERS_REQUEST:
      answer = self._handle_get_peers_request()
    elif event['event'] == Event.GET_PEERS_RESPONSE:
      asyncio.ensure_future(self._handle_get_peers_response(event['data']))
    elif event['event'] == Event.MY_ADDRESS:
      asyncio.ensure_future(self._handle_my_address(event['data'], websocket))
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

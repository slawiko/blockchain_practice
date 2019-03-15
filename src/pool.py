import json
import asyncio

from websockets.exceptions import ConnectionClosed

class Pool():
  def __init__(self):
    self._peers = dict()
  
  @property
  def addresses(self):
    return list(self._peers.keys())

  @property
  def connections(self):
    return list(self._peers.values())

  @property
  def peers(self):
    return self._peers

  async def register_connection(self, address, websocket, con_type):
    self._peers[address] = websocket
    print(f'Connection {con_type} {address} is registered ({websocket.local_address}:{websocket.remote_address})')
    asyncio.ensure_future(self.unregister_connection(address))

  async def unregister_connection(self, address, reason='closed'):
    await self._peers[address].wait_closed()
    del self._peers[address]
    print(f'{address} is unregistered. Reason: {reason}')

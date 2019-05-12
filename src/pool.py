import json
import logging
import asyncio

from websockets.exceptions import ConnectionClosed

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Pool:
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
        log.info(
            f'Connection {con_type} {address} is registered ({websocket.local_address}:{websocket.remote_address})')
        asyncio.ensure_future(self.unregister_connection(address))

    async def unregister_connection(self, address, reason='closed'):
        # TODO: websockets 6.0 do not have wait_closed() method in Protocol
        await self._peers[address].wait_closed()
        del self._peers[address]
        log.info(f'{address} is unregistered. Reason: {reason}')

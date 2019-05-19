import logging
import asyncio

from websockets.exceptions import ConnectionClosed

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Pool:
    def __init__(self):
        self._peers = {}
        self._remote_addresses = {}

    @property
    def actual_addresses(self):
        return list(self._peers.keys())

    @property
    def connections(self):
        return list(self._peers.values())

    @staticmethod
    def actual_address(port, websocket):
        return websocket.remote_address[0], port

    def get_all_except(self, websocket):
        clean_addresses = list(self.actual_addresses)
        clean_addresses.remove(self._remote_addresses[websocket.remote_address])

        return clean_addresses

    async def register_connection(self, address, websocket):
        self._peers[address] = websocket
        log.info(
            f'Connection from {address} is registered ({websocket.local_address}:{websocket.remote_address})')
        asyncio.ensure_future(self.unregister_connection(address))
        self._remote_addresses[websocket.remote_address] = address

    async def unregister_connection(self, address, reason='closed'):
        # TODO: websockets 6.0 do not have wait_closed() method in Protocol
        await self._peers[address].wait_closed()
        del self._peers[address]
        log.info(f'{address} is unregistered. Reason: {reason}')

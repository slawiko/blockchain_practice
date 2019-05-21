import logging

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

    def get_actual_address(self, websocket):
        if websocket.remote_address in self._remote_addresses:
            return self._remote_addresses[websocket.remote_address]
        else:
            return 'unknown'

    def get_all_except(self, websocket):
        clean_addresses = list(self.actual_addresses)
        clean_addresses.remove(self._remote_addresses[websocket.remote_address])

        return clean_addresses

    async def register_connection(self, address, websocket):
        self._peers[address] = websocket
        log.info(
            f'Connection from {address} is registered')
        self._remote_addresses[websocket.remote_address] = address

    def unregister_connection(self, websocket, reason):
        address = self._remote_addresses[websocket.remote_address]
        del self._peers[address]
        del self._remote_addresses[websocket.remote_address]
        log.info(f'{address} is unregistered. Reason: {reason}')

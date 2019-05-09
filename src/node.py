import json
import asyncio
import logging

import websockets
from websockets.exceptions import ConnectionClosed

from pool import Pool
from event import Event
from blockchain import Blockchain
from transaction import create

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def parse_ip(ip):
    parts = ip.split(':')
    return parts[0], int(parts[1]) if len(parts) > 1 else 80


class Node:
    def __init__(self, seeds, ip='127.0.0.1', port=8765, auto_discovering=True, auto_discovering_interval=60):
        self.address = (ip, int(port))
        self.blockchain = Blockchain()
        self._auto_discovering = auto_discovering
        self._auto_discovering_interval = auto_discovering_interval
        self._seeds = seeds
        self._pool = Pool()

    async def start(self):
        await websockets.serve(self._listen_incoming, self.address[0], self.address[1])
        log.info(f'ws server started at {self.address[0]}:{self.address[1]}')
        await self._connect(self._seeds)
        log.info(f'ws server connected to peers')
        if self._auto_discovering:
            await self._start_auto_discover()
            log.info(f'auto discovering started')

    async def _connect(self, addresses):
        for address in map(parse_ip, addresses):
            websocket = await websockets.connect(f'ws://{address[0]}:{address[1]}')
            await self._listen_outgoing(websocket, address)

    async def broadcast(self, event):
        tasks = [Node.send(connection, event) for connection in self._pool.connections]
        if len(tasks) > 0:
            log.info(f'broadcast on {len(tasks)} peers')
            await asyncio.gather(*tasks)
        else:
            log.warning(f'no one to broadcast event {event}')

    async def _start_auto_discover(self):
        async def get_new_peers():
            event = Event.construct(Event.GET_PEERS_REQUEST)
            while True:
                await asyncio.sleep(self._auto_discovering_interval)
                await self.broadcast(event)

        try:
            asyncio.get_event_loop().create_task(get_new_peers())
        except Exception as error:
            log.error(f'unable to connect. {error}')

    async def _listen(self, websocket, uri=''):
        while True:
            message = await websocket.recv()
            log.info(f'Received {message} from {websocket.local_address}:{websocket.remote_address}')
            answer = await self._handle_message(message, websocket)
            if answer:
                await Node.send(websocket, answer)
                log.info(f'Sent {answer} to {websocket.local_address}')

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
            log.info(f'New peers found: {new_addresses}')
            await self._connect(new_addresses)
        log.info(f'No new peers found')

    async def _handle_my_address(self, data, websocket):
        address = tuple(data)
        await self._pool.register_connection(address, websocket, 'from')

    async def _handle_add_transaction(self, data, signature):
        await self.add_transaction(data, signature)

    async def create_transaction(self, data):
        transaction, signature = create(data)
        return await self.add_transaction(transaction, signature)

    async def add_transaction(self, transaction, signature):
        done = self.blockchain.add_transaction(transaction, signature)
        if done:
            event = Event.construct(Event.ADD_TRANSACTION, transaction, signature)
            await self.broadcast(event)
            return done

    def get_transactions(self):
        return self.blockchain.transactions

    def public_key(self):
        return self.blockchain.public_key.to_string()

    async def _handle_message(self, message, websocket):
        # TODO: json is not working here because data can be bytes
        event = json.loads(message)
        answer = None
        if event['event'] == Event.GET_PEERS_REQUEST:
            answer = self._handle_get_peers_request()
        elif event['event'] == Event.GET_PEERS_RESPONSE:
            asyncio.ensure_future(self._handle_get_peers_response(event['data']))
        elif event['event'] == Event.MY_ADDRESS:
            asyncio.ensure_future(self._handle_my_address(event['data'], websocket))
        elif event['event'] == Event.ADD_TRANSACTION:
            asyncio.ensure_future(self._handle_add_transaction(event['data'], event['sign']))
        else:
            log.warning(f'Unknown event {event}')
        return answer

    @staticmethod
    async def send(websocket, message):
        try:
            log.info(f'Sending {message} to {websocket.local_address}:{websocket.remote_address}')
            await websocket.send(message)
        except ConnectionClosed as cc:
            log.info(f'Connection to {websocket} is closed. {cc}')
        except Exception as e:
            log.error(f'Unexpected error occurred during send {e}')

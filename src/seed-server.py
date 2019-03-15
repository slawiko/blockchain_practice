import asyncio
import os
import logging

from ws import Node

logging.basicConfig(level=logging.WARNING)

def parse_ip(ip):
  parts = ip.split(':')
  return (parts[0], int(parts[1]) if len(parts) > 1 else 80)

def parse_addresses(seeds):
  parts = seeds.split(',')
  addresses = parts if len(parts[0]) > 0 else []
  parsed = list(map(parse_ip, addresses))
  return parsed

PORT = os.environ.get('PORT') or 8765
SEEDS = [] if not os.environ.get('SEEDS') else parse_addresses(os.environ.get('SEEDS'))

loop = asyncio.get_event_loop()

node = Node(SEEDS, port=PORT)
loop.create_task(node.start())
loop.run_forever()


import asyncio
import os
import logging

from sanic import Sanic, response

from node import Node

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

def main(loop):
  node = Node(SEEDS, port=PORT)

  app = Sanic()
  @app.route('/transactions/new', methods=['POST'])
  async def new_transaction(request):
    data = request.json
    print(data)
    # TODO initiator
    result = await node.add_transaction(data)
    if result:
      message = 'Transaction will be added'
    else:
      message = 'Transaction will not be added'

    return response.json({ 'message': message })

  @app.route('/transactions')
  def get_transactions(request):
    transactions = node.get_transactions()
    return response.json({ 'transactions': transactions })

  # @app.route('/mine', methods=['POST'])
  # def mine():
  #   if blockchain.add_block():
  #     message = 'Mining is succeed'
  #     status = 200
  #   else:
  #     message = 'Mining is failed'
  #     status = 500
    
  #   response = { 'message': message }
  #   return jsonify(response), status

  # @app.route('/', methods=['GET'])
  # def debug():
  #   return jsonify({ 'blockchain': blockchain.chain, 'transactions': blockchain.transactions }), 200

  app.add_task(node.start())
  app.run(host="127.0.0.1", port=8080)

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  try:
    main(loop)
  except KeyboardInterrupt:
    print(f'Exited by user')
  finally:
    loop.close()
else:
  raise ImportError('script can not be imported')
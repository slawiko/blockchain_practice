import asyncio
import argparse
import logging

from sanic import Sanic, response

from node import Node

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description='Run node', add_help=True)

parser.add_argument('--interface-port', metavar='i_port', type=int, nargs='?', dest='i_port', default=8080,
                    help='port for interface')
parser.add_argument('--node-port', metavar='n_port', type=int, nargs='?', dest='n_port', default=8765,
                    help='port for blockchain node')
parser.add_argument('--seeds', metavar='SEEDS', type=str, nargs='*', dest='seeds', default=[],
                    help='list of seeds blockchain will connect to')

args = parser.parse_args()


def main(loop):
    node = Node(args.seeds, port=args.n_port)

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

        return response.json({'message': message})

    @app.route('/transactions')
    def get_transactions(request):
        transactions = node.get_transactions()
        return response.json({'transactions': transactions})

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
    app.run(host="127.0.0.1", port=args.i_port)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        main(loop)
    except KeyboardInterrupt:
        log.info(f'Exited by user')
    finally:
        loop.close()
else:
    raise ImportError('script can not be imported')

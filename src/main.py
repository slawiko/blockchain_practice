import argparse
import logging
import json

from sanic import Sanic, response

from node import Node
from transaction import Transaction

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


def custom_dumps(transactions):
    if all(isinstance(t, Transaction) for t in transactions):
        return json.dumps(list(map(Transaction.dumps, transactions)))

    raise TypeError('only list of Transactions is supported')


def main(node):
    app = Sanic()

    @app.route('/transactions/new', methods=['POST'])
    async def new_transaction(request):
        data = request.body

        result = await node.create_transaction(data)
        if result:
            message = 'Transaction will be added'
        else:
            message = 'Transaction will not be added'

        return response.json({'message': message})

    @app.route('/transactions')
    def get_transactions(request):
        transactions = node.get_transactions()
        return response.json(transactions, dumps=custom_dumps)

    @app.route('/public-key', methods=['GET'])
    def get_public_key(request):
        return response.text(node.public_key())

    app.add_task(node.start())
    app.run(host="0.0.0.0", port=args.i_port)


if __name__ == '__main__':
    main(Node(args.seeds, port=args.n_port))

else:
    raise ImportError('script can not be imported')

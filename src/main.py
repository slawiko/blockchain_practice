import argparse
import logging
import json

from sanic import Sanic, response

from node import Node
from blockchain.transaction import Transaction
from blockchain.block import Block

logging.basicConfig(level=logging.INFO)
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


def dump_transactions(transactions):
    if all(isinstance(t, Transaction) for t in transactions.values()):
        return json.dumps(list(map(Transaction.dumps, transactions.values())))

    raise TypeError('only dict of Transactions is supported')


def dump_blocks(blocks):
    if all(isinstance(t, Block) for t in blocks):
        return json.dumps(list(map(Block.dumps, blocks)))

    raise TypeError('only list of Blocks is supported')


def main(node):
    app = Sanic()

    @app.route('/transactions/new', methods=['POST'])
    async def new_transaction(request):
        data = request.body

        try:
            await node.create_transaction(data)
        except ValueError:
            res = {'error': 'Transaction will not be added'}
            status = 422
        except BaseException as e:
            log.error(e)
            res = {'error': 'Transaction will not be added'}
            status = 500
        else:
            res = {'message': 'Transaction will be added'}
            status = 200

        return response.json(res, status=status)

    @app.route('/transactions')
    def get_transactions(request):
        transactions = node.get_transactions()
        return response.json(transactions, dumps=dump_transactions)

    @app.route('/blocks')
    def get_blocks(request):
        blocks = node.get_blocks()
        return response.json(blocks, dumps=dump_blocks)

    @app.route('/mine', methods=['POST'])
    def mine(request):
        try:
            node.mine()
            res = {'message': f'Block is mined successfully'}
            status = 200
        except BaseException as e:
            log.error(e)
            res = {'message': 'Error occurred during mining'}
            status = 500

        return response.json(res, status=status)

    @app.route('/public-key', methods=['GET'])
    def get_public_key(request):
        return response.text(node.public_key())

    app.add_task(node.start())
    app.run(host="0.0.0.0", port=args.i_port)


if __name__ == '__main__':
    main(Node(args.seeds, port=args.n_port))

else:
    raise ImportError('script can not be imported')

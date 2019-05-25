from .block import Block
from .transaction import Transaction


def is_valid_chain(chain):
    if chain[0] != Block.genesis():
        return False

    for i in range(1, len(chain)):
        previous = chain[i - 1]
        current = chain[i]
        if current.previousHash != previous.hash():
            return False

    return True


class Blockchain:
    def __init__(self):
        self.chain = []
        self.chain.append(Block.genesis())
        self.transactions = {}

    def add_transaction(self, transaction, signature):
        if not Transaction.is_valid(transaction, signature):
            raise ValueError('Transaction is not valid')

        if transaction.digest in self.transactions:
            raise ValueError('Transaction already exists')

        self.transactions[transaction.digest] = transaction

    def add_block(self):
        if len(self.transactions) == 0:
            return False

        self.chain.append(Block(self.last_block_hash, self.transactions))
        self.transactions = {}

        return self.last_block_hash

    def replace_chain(self, chain):
        if len(chain) <= len(self.chain):
            raise ValueError('New chain must be longer than old one')

        self.chain = chain

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def last_block_hash(self):
        return self.last_block.calculateHash()

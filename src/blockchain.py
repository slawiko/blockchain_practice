import hashlib
import json
from time import time

from block import Block


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
        self.transactions = []

    def add_transaction(self, initiator, data):
        # TODO nice way for not-adding existing transactions
        transaction = {
            'initiator': initiator,
            'data': data
        }
        if transaction in self.transactions:
            return False

        self.transactions.append(transaction)
        return True

    def add_block(self):
        if len(self.transactions) == 0:
            return False

        self.chain.append(Block(self.last_block_hash, self.transactions))
        self.transactions = []

        return self.last_block_hash

    def replace_chain(self, chain):
        if len(chain) <= len(self.chain):
            raise ValueError('New chain must be greater than old one')

        self.chain = chain

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def last_block_hash(self):
        return self.last_block.calculateHash()

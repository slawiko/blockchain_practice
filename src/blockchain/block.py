import hashlib
import logging

from blockchain.transaction import Transaction

complexity = 5
log = logging.getLogger(__name__)


class Block:
    def __init__(self, previous_hash, transactions, nonce=None, block_hash=None):
        self.previousHash = previous_hash
        # TODO: merkle tree?
        self.transactions = transactions
        self.nonce = nonce or 0
        self.hash = block_hash or self.calculate_hash()

    def calculate_hash(self):
        # TODO: merkle tree root?
        data = f"{self.previousHash}\n{','.join(self.transactions.keys())}\n"
        prefix = '0' * complexity

        with_nonce = f'{data}{self.nonce}'.encode('utf-8')
        digest = hashlib.sha256(with_nonce).hexdigest()

        while digest[:complexity] != prefix:
            self.nonce += 1
            with_nonce = f'{data}{self.nonce}'.encode('utf-8')
            digest = hashlib.sha256(with_nonce).hexdigest()

        log.info('Hash found!')
        return digest

    def sign(self, private):
        return private.sign(self.digest)

    @property
    def digest(self):
        h = self.__hash()
        return h.digest()

    def hexdigest(self):
        return self.__hash().hexdigest()

    def __hash(self):
        data = f"{self.previousHash}\n{','.join(self.transactions.keys())}\n{self.nonce}".encode('utf-8')
        return hashlib.sha256(data)

    @staticmethod
    def dumps(block):
        return {
            "transactions": list(map(Transaction.dumps, block.transactions.values())),
            "previousHash": block.previousHash,
            "nonce": block.nonce,
            "hash": block.hash
        }

    @staticmethod
    def genesis():
        return Block('', {}, 523782, '000004c41d6eccd35e6bb5f8220cc8f22d68d911af276a060d80fbaf6c647df6')

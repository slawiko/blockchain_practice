import hashlib
import json
from time import time

genesis = {
  'index': 0,
  'timestamp': time(),
  'transactions': (),
  'previous_hash': '0'
}

class Blockchain:
  def __init__(self):
    self.chain = []
    self.chain.append(genesis)
    self.transactions = []

  def add_transaction(self, actor, signature):
    self.transactions.append({
      'actor': actor,
      'action': 'allow',
      'signature': signature
    })

    return True

  def add_block(self, proof):
    if not self.is_valid_proof(proof):
      return False
    
    block = {
      'index': self.last_block['index'] + 1,
      'timestamp': time(),
      'transactions': tuple(self.transactions),
      'proof': proof,
      'previous_hash': self.last_block_hash
    }

    self.chain.append(block)
    self.transactions = []

    return self.last_block_hash

  def is_valid_proof(self, proof):
    guess = f'{proof}{self.last_block_hash}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    result = guess_hash[:2] == '00'
    print(f'Proof has {guess_hash} as hash and it\'s {result}')
    return result

  @staticmethod
  def hash(block):
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode('utf-8')).hexdigest()

  @property
  def last_block(self):
    return self.chain[-1]

  @property
  def last_block_hash(self):
    return self.hash(self.last_block)

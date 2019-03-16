import hashlib
from time import time
import json
# from flask.json import JSONEncoder

# class BlockJSONEncoder(JSONEncoder):
#   def default(self, obj):
#     if isinstance(obj, Block):
#       return obj.to_dict()
    
#     return super.default(self, obj)

class Block:
  def __init__(self, previousHash, transactions, timestamp=time()):
    self.previousHash = previousHash
    self.transactions = transactions
    self.timestamp = timestamp
    self.hash = self.calculateHash()

  def calculateHash(self):
    # TODO: transactions can raise here an error
    data = f'{self.timestamp}\n{self.previousHash}\n{self.transactions}'.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

  def to_dict(self):
    return {
      "timestamp": self.timestamp,
      "transactions": self.transactions,
      "previousHash":  self.previousHash,
      "hash": self.hash
    }

  @staticmethod
  def genesis():
    return Block('', [], 0)

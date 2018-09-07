from flask import Flask, request, jsonify
from urllib.parse import urlparse
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()
nodes = set()

def register_node(address):
  nodes.add(urlparse(address).netloc)

def validate_chain(chain):
  current_index = 1
  previous_block = chain[current_index - 1]

  while current_index < len(chain):
    current_block = chain[current_index]

    if current_block['previous_hash'] != 

def POW(chain):
  proof = 0
  while not chain.is_valid_proof(proof):
    proof += 1
  
  return proof

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
  data = request.get_json()
  print(data)
  if blockchain.add_transaction(data['sender'], data['recipient']):
    message = 'Transaction will be added'
    status = 200
  else:
    message = 'Transaction will not be added'
    status = 500

  response = { 'message': message }
  return jsonify(response), status

@app.route('/mine', methods=['POST'])
def mine():
  proof = POW(blockchain)
  if blockchain.add_block(proof):
    message = 'Mining is succeed'
    status = 200
  else:
    message = 'Mining is failed'
    status = 500
  
  response = { 'message': message }
  return jsonify(response), status

@app.route('/', methods=['GET'])
def debug():
  return jsonify({ 'blockchain': blockchain.chain, 'transactions': blockchain.transactions }), 200

app.run(host='127.0.0.1', port=8080)
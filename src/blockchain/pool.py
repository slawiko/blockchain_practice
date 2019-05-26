from blockchain.transaction import Transaction


class TransactionPool:
    def __init__(self):
        self._transactions = {}

    def add_transaction(self, transaction, signature):
        if not Transaction.is_valid(transaction, signature):
            raise ValueError('Transaction is not valid')

        if transaction.digest in self._transactions:
            raise ValueError('Transaction already exists')

        self._transactions[transaction.digest] = transaction

    def get_transactions(self, resolver=None):
        return self._transactions

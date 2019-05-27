from blockchain.transaction import Transaction


class TransactionPool:
    def __init__(self):
        self._transactions = {}

    def add_transaction(self, transaction, signature):
        if not Transaction.is_valid(transaction, signature):
            raise ValueError('Transaction is not valid')

        if transaction.digest in self._transactions:
            raise ValueError('Transaction already exists')

        self._transactions[transaction.hexdigest()] = transaction

    def get_transactions(self, resolver=None):
        return self._transactions

    def pop_transactions(self, resolver=None):
        transactions = self._transactions.copy()
        for transaction in transactions.keys():
            del self._transactions[transaction]
        return transactions

    def push_transactions(self, transactions):
        self._transactions.update(transactions)

    def remove_transactions(self, transactions):
        digests_to_remove = transactions.keys()
        for digest in digests_to_remove:
            self._transactions.pop(digest, None)

import logging
import hashlib

import ecdsa

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Transaction:
    def __init__(self, data, public):
        self.public = public.to_string()
        self.data = data

    def sign(self, private):
        return private.sign(self.digest)

    def __hash(self):
        h = hashlib.sha512()
        h.update(self.data)
        h.update(self.public)
        return h

    @property
    def digest(self):
        return self.__hash().digest()

    def hexdigest(self):
        return self.__hash().hexdigest()

    @staticmethod
    def dumps(transaction):
        return {
            "public": transaction.public.hex(),
            "data": transaction.data.decode('utf-8'),
            "hash": transaction.hexdigest()
        }

    @staticmethod
    def is_valid(transaction, signature):
        return verify(transaction.public, transaction.digest, signature)


def verify(public_key, data, signature):
    vk = ecdsa.VerifyingKey.from_string(public_key)
    try:
        vk.verify(signature, data)
        return True
    except ecdsa.BadSignatureError:
        return False

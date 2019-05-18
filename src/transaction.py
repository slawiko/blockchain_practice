import pickle
import os
import logging
import hashlib

import ecdsa

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

private, public = None, None


def keys():
    global private
    global public

    path = 'keys.dat'
    if not os.path.isfile(path):
        log.info(f'cannot find key dump file {path}. Creating new')
        private, public = generate_keys()
        with open(path, 'wb') as f:
            pickle.dump((private, public), f)
    else:
        log.info(f'key dump file {path} found')
        with open(path, 'rb') as f:
            private, public = pickle.load(f)

    return private, public


def generate_keys():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p)
    vk = sk.get_verifying_key()
    return sk, vk


class Transaction:
    def __init__(self, data):
        if not public or not private:
            raise Exception('private/public key pair need to be initialized first')

        self.public = public.to_string()
        self.data = data

    def sign(self):
        if not public or not private:
            raise Exception('private/public key pair need to be initialized first')

        return private.sign(self.digest)

    def __hash(self):
        h = hashlib.sha512()
        h.update(self.data)
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
        vk = ecdsa.VerifyingKey.from_string(transaction.public)
        try:
            vk.verify(signature, transaction.digest)
            return True
        except ecdsa.BadSignatureError:
            return False

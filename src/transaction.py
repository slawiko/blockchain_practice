import pickle
import os
import logging
from enum import EnumMeta

import ecdsa

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TransactionFields(EnumMeta):
    PUBLIC = 'public'
    DATA = 'data'


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


def is_valid(transaction, signature):
    vk = ecdsa.VerifyingKey.from_string(transaction[TransactionFields.PUBLIC])
    try:
        vk.verify(signature, transaction[TransactionFields.DATA])
        return True
    except ecdsa.BadSignatureError:
        return False


def create(data):
    if not public or not private:
        raise Exception('private/public key pair need to be initialized first')

    transaction = {
        TransactionFields.PUBLIC: public.to_string(),
        TransactionFields.DATA: data
    }
    signature = private.sign(data)

    return transaction, signature

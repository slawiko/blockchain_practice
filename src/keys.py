import pickle
import os
import logging

import ecdsa

log = logging.getLogger(__name__)


def keys(path='data/keys.dat'):
    if os.path.isfile(path):
        log.info(f'key dump file {path} found')
        with open(path, 'rb') as f:
            private, public = pickle.load(f)
    else:
        log.info(f'cannot find key dump file {path}. Creating new')
        private, public = generate_keys()
        with open(path, 'wb') as f:
            pickle.dump((private, public), f)

    return private, public


def generate_keys():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST192p)
    vk = sk.get_verifying_key()
    return sk, vk


def verify(public_key, data, signature):
    vk = ecdsa.VerifyingKey.from_string(public_key)
    try:
        vk.verify(signature, data)
        return True
    except ecdsa.BadSignatureError:
        return False

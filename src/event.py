import pickle
from enum import EnumMeta


class Event(EnumMeta):
    MY_ADDRESS = 'MY_ADDRESS'
    GET_PEERS_REQUEST = 'GET_PEERS_REQUEST'
    GET_PEERS_RESPONSE = 'GET_PEERS_RESPONSE'
    ADD_TRANSACTION = 'ADD_TRANSACTION'

    @staticmethod
    def parse(serialized_event):
        return pickle.loads(serialized_event)

    @staticmethod
    def construct(event_type, data=None, signature=None):
        event = {'type': event_type}
        if data is not None:
            event['data'] = data

        if signature:
            event['sign'] = signature

        return pickle.dumps(event)

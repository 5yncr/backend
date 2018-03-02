from abc import ABC
from abc import abstractmethod


class PublicKeyStore(ABC):
    @abstractmethod
    def set_key(self, key):
        pass

    @abstractmethod
    def request_key(self, request_node_id):
        pass

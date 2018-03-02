from abc import ABC
from abc import abstractmethod


class DropPeerStore(ABC):

    @abstractmethod
    def add_drop_peer(self, drop_id, ip, port):
        pass

    @abstractmethod
    def request_peers(self, drop_id):
        pass

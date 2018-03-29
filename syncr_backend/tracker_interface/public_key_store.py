"""Functionality to get public keys from a public key store"""
from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Tuple

from syncr_backend.constants import TRACKER_OK_RESULT
from syncr_backend.constants import TRACKER_REQUEST_GET_KEY
from syncr_backend.constants import TRACKER_REQUEST_POST_KEY
from syncr_backend.tracker_interface.tracker_util import (
    send_request_to_tracker
)


class PublicKeyStore(ABC):
    """Abstract base class for storage and retrieval of public keys"""

    @abstractmethod
    def set_key(self, key):
        pass

    @abstractmethod
    def request_key(self, request_node_id):
        pass


class TrackerKeyStore(PublicKeyStore):
    """Tracker based implementation of the public key store"""

    def __init__(self, node_id: bytes, ip: str, port: int) -> None:
        """
        Sets up a TrackerKeyStore with the trackers ip and port and the id of
        the given node
        :param node_id: SHA256 hash
        :param ip: string of ipv4 or ipv6
        :param port: port for the tracker connection
        """
        self.node_id = node_id
        self.tracker_ip = ip
        self.tracker_port = port

    def set_key(self, key: bytes) -> bool:
        """
        Sets the public key of the this node on the tracker
        :param key: 4096 RSA public key
        :return: boolean on success of setting key
        """
        request = {
            'request_type': TRACKER_REQUEST_POST_KEY,
            'node_id': self.node_id,
            'data': key,
        }

        response = send_request_to_tracker(
            request, self.tracker_ip,
            self.tracker_port,
        )
        if response.get('result') == TRACKER_OK_RESULT:
            print(response.get('message'))
            return True
        else:
            print(response.get('message'))
            return False

    def request_key(
        self, request_node_id: bytes,
    ) -> Tuple[bool, Optional[str]]:
        """
        Asks tracker for the public key of a given node for sake of signature
        verification
        :param request_node_id: SHA256 hash
        :return: boolean (success of getting key),
                2048 RSA public key (if boolean is True)
        """
        request = {
            'request_type': TRACKER_REQUEST_GET_KEY,
            'node_id': request_node_id,
        }

        response = send_request_to_tracker(
            request, self.tracker_ip,
            self.tracker_port,
        )
        if response.get('result') == TRACKER_OK_RESULT:
            print(response.get('message'))
            return True, response.get('data')
        else:
            print(response.get('message'))
            return False, 'NO PUBLIC KEY AVAILABLE'

from typing import Tuple

from syncr_backend.constants import TRACKER_OK_RESULT
from syncr_backend.PublicKeyStore import PublicKeyStore
from syncr_backend.tracker_util import send_request_to_tracker


class TrackerKeyStore(PublicKeyStore):

    def __init__(self, node_id: bytes, ip: str, port: int) -> None:
        """
        Sets up a TrackerKeyStore with the trackers ip and port and the id of
        the given node
        :param node_id: SHA256 hash
        :param ip: string of ipv4 or ipv6
        :param port: port for the tracker connection
        """
        self.node_id = node_id
        self.TRACKER_IP = ip
        self.TRACKER_PORT = port

    def set_key(self, key: bytes) -> bool:
        """
        Sets the public key of the this node on the tracker
        :param key: 2048 RSA public key
        :return: boolean dependant on the tracker response
        """
        request = ['POST', self.node_id, key]

        response = send_request_to_tracker(
            request, self.TRACKER_IP,
            self.TRACKER_PORT,
        )
        if response.get('result') == TRACKER_OK_RESULT:
            print(response.get('message'))
            return True
        else:
            print(response.get('message'))
            return False

    def request_key(self, request_node_id: bytes) -> Tuple[bool, bytes]:
        """
        Asks tracker for the public key of a given node for sake of signature
        verification
        :param request_node_id: SHA256 hash
        :return: boolean, 2048 RSA public key (if boolean is True)
        """
        request = ['GET', request_node_id]

        response = send_request_to_tracker(
            request, self.TRACKER_IP,
            self.TRACKER_PORT,
        )
        if response.get('result') == TRACKER_OK_RESULT:
            print(response.get('message'))
            return True, response.get('data')
        else:
            print(response.get('message'))
            return False, 'NO PUBLIC KEY AVAILABLE'

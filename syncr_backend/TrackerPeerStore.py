from typing import Tuple

import DropPeerStore
from constants import TRACKER_OK_RESULT
from tracker_util import send_request_to_tracker


class TrackerPeerStore(DropPeerStore):

    def __init__(self, node_id: bytes, ip: str, port: int):
        """
        Sets up a TrackerPeerStore with the trackers ip and port and the id of
        the given node
        :param node_id: SHA256 hash
        :param ip: string of ipv4 or ipv6
        :param port: port for the tracker connection
        """
        self.node_id = node_id
        self.TRACKER_IP = ip
        self.TRACKER_PORT = port

    def add_drop_peer(self, drop_id: bytes, ip: str, port: int) -> bool:
        """
        Adds their node_id, ip, and port to a list of where a given drop is
        available
        :param drop_id: node_id (SHA256 hash) + SHA256 hash
        :param ip: string of ipv4 or ipv6
        :param port: port where drop is being hosted
        :return:
        """
        request = ['POST', drop_id, [self.node_id, ip, port]]

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

    def request_peers(self, drop_id: bytes) -> Tuple[bool, list]:
        """
        Asks tracker for the nodes and their ip ports for a specified drop
        :param drop_id: node_id (SHA256 hash) + SHA256 hash
        :return: boolean, list of [node_id, ip, port]
        """
        request = ['GET', drop_id]

        response = send_request_to_tracker(
            request, self.TRACKER_IP,
            self.TRACKER_PORT,
        )
        if response.get('result') == TRACKER_OK_RESULT:
            print(response.get('message'))
            return True, response.get('data')
        else:
            print(response.get('message'))
            return False, list()

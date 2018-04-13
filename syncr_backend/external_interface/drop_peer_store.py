"""Functionality to get peers from a peer store"""
import asyncio
import json
import os
import threading
import time
from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Tuple

from syncr_backend.constants import DEFAULT_DPS_CONFIG_FILE
from syncr_backend.constants import TRACKER_DROP_AVAILABILITY_TTL
from syncr_backend.constants import TRACKER_OK_RESULT
from syncr_backend.constants import TRACKER_REQUEST_GET_PEERS
from syncr_backend.constants import TRACKER_REQUEST_POST_PEER
from syncr_backend.external_interface.dht_util import \
    get_dht
from syncr_backend.external_interface.store_exceptions import \
    IncompleteConfigError
from syncr_backend.external_interface.store_exceptions import \
    MissingConfigError
from syncr_backend.external_interface.store_exceptions import \
    UnsupportedOptionError
from syncr_backend.external_interface.tracker_util import \
    send_request_to_tracker
from syncr_backend.init.node_init import get_full_init_directory
from syncr_backend.init.node_init import load_private_key_from_disk
from syncr_backend.metadata.drop_metadata import list_drops
from syncr_backend.util import crypto_util
from syncr_backend.util.crypto_util import node_id_from_private_key
from syncr_backend.util.log_util import get_logger


logger = get_logger(__name__)


def send_drops_to_dps(
    ip: str,
    port: int,
    shutdown_flag: threading.Event,
) -> None:
    this_node_id = node_id_from_private_key(load_private_key_from_disk())
    dps = get_drop_peer_store(this_node_id)

    while not shutdown_flag.is_set():
        drops = list_drops()
        logger.info("Sending drops to dps")
        for drop in drops:
            logger.debug("Sending drop %s", crypto_util.b64encode(drop))
            dps.add_drop_peer(drop, ip, port)
        sleep_time = TRACKER_DROP_AVAILABILITY_TTL / 2 - 1
        logger.debug("Sleeping for %s", sleep_time)
        time.sleep(sleep_time)


def get_drop_peer_store(node_id: bytes) -> "DropPeerStore":
    """
    Provides a DropPeerStore either by means of DHT or tracker depending
    on config file
    :param node_id: bytes of the node id for this node
    :return: DropPeerStore
    """
    init_directory = get_full_init_directory(None)
    dps_config_path = os.path.join(init_directory, DEFAULT_DPS_CONFIG_FILE)

    if not os.path.isfile(dps_config_path):
        raise MissingConfigError()

    config_file = json.load(open(dps_config_path))

    try:
        if config_file['type'] == 'tracker':
            pks = TrackerPeerStore(
                node_id, config_file['ip'], int(config_file['port']),
            )
            return pks
        elif config_file['type'] == 'dht':
            return DHTPeerStore(
                node_id,
                list(
                    zip(
                        config_file['bootstrap_ips'],
                        config_file['bootstrap_ports'],
                    ),
                ),
                config_file['listenport'],
            )
        else:
            raise UnsupportedOptionError()
    except KeyError:
        raise IncompleteConfigError()


class DropPeerStore(ABC):
    """Abstract base class for communication to send/get peer lists"""

    @abstractmethod
    def add_drop_peer(self, drop_id: bytes, ip: str, port: int) -> bool:
        pass

    @abstractmethod
    def request_peers(
        self, drop_id: bytes,
    ) -> Tuple[bool, List[Tuple[bytes, str, int]]]:
        pass


class DHTPeerStore(DropPeerStore):
    def __init__(
        self,
        node_id: bytes,
        bootstrap_list: List[Tuple[str, int]],
        listen_port: int,
    ) -> None:
        """
        Sets up DHT peer store
        :param node_id: node_id of this node
        :param bootstrap_list: list of ip,port to bootstrap connect to dht
        """
        self.node_id = node_id
        self.listen_port = listen_port
        self.node_instance = get_dht(bootstrap_list, listen_port)

    def add_drop_peer(self, drop_id: bytes, ip: str, port: int) -> bool:
        """
        Add entry to dht
        :param drop_id: drop_id entry to update
        :param ip: ip to recieve requests regarging drop on
        :param port: port to recieve requests regarging drop on
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                self.node_instance.set(drop_id, [self.node_id, ip, port]),
            )
            return True
        except Exception:
            return False

    def request_peers(
        self, drop_id: bytes,
    ) -> Tuple[bool, List[Tuple[bytes, str, int]]]:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.node_instance.get(drop_id))
        if result is not None:
            return True, result
        else:
            return False, []


class TrackerPeerStore(DropPeerStore):
    """Implementation of Peer Store communication using a tracker"""

    def __init__(self, node_id: bytes, ip: str, port: int) -> None:
        """
        Sets up a TrackerPeerStore with the trackers ip and port and the id of
        the given node
        :param node_id: SHA256 hash
        :param ip: string of ipv4 or ipv6
        :param port: port for the tracker connection
        """
        self.node_id = node_id
        self.tracker_ip = ip
        self.tracker_port = port

    def add_drop_peer(self, drop_id: bytes, ip: str, port: int) -> bool:
        """
        Adds their node_id, ip, and port to a list of where a given drop is
        available
        :param drop_id: node_id (SHA256 hash) + SHA256 hash
        :param ip: string of ipv4 or ipv6
        :param port: port where drop is being hosted
        :return: boolean on success of adding drop peer
        """
        request = {
            'request_type': TRACKER_REQUEST_POST_PEER,
            'drop_id': drop_id,
            'data': [self.node_id, ip, port],
        }

        response = send_request_to_tracker(
            request, self.tracker_ip,
            self.tracker_port,
        )
        logger.debug("tracker add peer response: %s", response)
        if response.get('result') == TRACKER_OK_RESULT:
            return True
        else:
            return False

    def request_peers(
        self, drop_id: bytes,
    ) -> Tuple[bool, List[Tuple[bytes, str, int]]]:
        """
        Asks tracker for the nodes and their ip ports for a specified drop
        :param drop_id: node_id (SHA256 hash) + SHA256 hash
        :return: boolean (success on receiving peers),
                list of [node_id, ip, port]
        """
        request = {
            'request_type': TRACKER_REQUEST_GET_PEERS,
            'drop_id': drop_id,
        }

        response = send_request_to_tracker(
            request, self.tracker_ip,
            self.tracker_port,
        )
        logger.debug("tracker get peers response: %s", response)
        if response.get('result') == TRACKER_OK_RESULT:
            data = response.get('data')
            if data is None:
                return False, []
            return True, data
        else:
            return False, []

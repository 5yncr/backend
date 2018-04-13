"""Functionality to get public keys from a public key store"""
import asyncio
import json
import os
from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import Tuple

from syncr_backend.constants import DEFAULT_PKS_CONFIG_FILE
from syncr_backend.constants import TRACKER_OK_RESULT
from syncr_backend.constants import TRACKER_REQUEST_GET_KEY
from syncr_backend.constants import TRACKER_REQUEST_POST_KEY
from syncr_backend.external_interface.distributed_hash_table_util import \
    get_dht
from syncr_backend.external_interface.store_exceptions import (
    IncompleteConfigError
)
from syncr_backend.external_interface.store_exceptions import (
    MissingConfigError
)
from syncr_backend.external_interface.store_exceptions import (
    UnsupportedOptionError
)
from syncr_backend.external_interface.tracker_util import (
    send_request_to_tracker
)
from syncr_backend.init.node_init import get_full_init_directory
from syncr_backend.util.log_util import get_logger


logger = get_logger(__name__)


def get_public_key_store(node_id: bytes) -> "PublicKeyStore":
    """
    Provides a PublicKeyStore either by means of DHT or tracker depending
    on config file
    :return: PublicKeyStore
    """
    init_directory = get_full_init_directory(None)
    pks_config_path = os.path.join(init_directory, DEFAULT_PKS_CONFIG_FILE)

    if not os.path.isfile(pks_config_path):
        raise MissingConfigError()

    config_file = json.load(open(pks_config_path))

    try:
        if config_file['type'] == 'tracker':
            pks = TrackerKeyStore(
                node_id, config_file['ip'], int(config_file['port']),
            )
            return pks
        elif config_file['type'] == 'dht':
            return DHTKeyStore(
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


class PublicKeyStore(ABC):
    """Abstract base class for storage and retrieval of public keys"""

    @abstractmethod
    def set_key(self, key):
        pass

    @abstractmethod
    def request_key(self, request_node_id):
        pass


class DHTKeyStore(PublicKeyStore):
    def __init__(
        self,
        node_id: bytes, bootstrap_list: List[Tuple[str, int]],
        listen_port: int,
    ) -> None:
        """
        Sets up tracker key store
        :param node_id: node id and SHA256 hash
        :param bootstrap_list: list of ip,port to bootstrap connect to dht
        """
        self.node_id = node_id
        self.node_instance = get_dht(bootstrap_list, listen_port)

    def set_key(self, key: bytes):
        """
        Sets the public key of the this node on the DHT
        :param key: 4096 RSA public key
        :return: boolean on success of setting key
        """
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                self.node_instance.set(self.node_id, key),
            )
            return True
        except Exception:
            return False

    def request_key(self, request_node_id: bytes,):
        """
        Asks DHT for the public key of a given node for sake of signature
        verification
        :param request_node_id: SHA256 hash
        :return: boolean (success of getting key),
                2048 RSA public key (if boolean is True)
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.node_instance.get(request_node_id),
        )
        if result is not None:
            return True, result
        else:
            return False, []


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
        logger.debug("tracker set key response: %s", response)
        if response.get('result') == TRACKER_OK_RESULT:
            return True
        else:
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
        logger.debug("tracker get key response: %s", response)
        if response.get('result') == TRACKER_OK_RESULT:
            return True, response.get('data')
        else:
            return False, 'NO PUBLIC KEY AVAILABLE'

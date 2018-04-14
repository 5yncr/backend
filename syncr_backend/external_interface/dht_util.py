import asyncio
import time
from collections import OrderedDict
from typing import Any
from typing import List
from typing import Tuple

from kademlia.network import Server  # type: ignore
from kademlia.storage import IStorage  # type: ignore

from syncr_backend.constants import TRACKER_DROP_AVAILABILITY_TTL
from syncr_backend.util.log_util import get_logger


logger = get_logger(__name__)

_node_instance = None


def get_dht(
    bootstrap_ip_port_pair_list: List[Tuple[str, int]],
    listen_port: int,
):
    """
    returns the node_instance of the dht
    if no node instance has been created it
    connects to the distributed hash table
    if no bootstrap ip port pair list is given, it starts a new dht
    :param bootstrap_ip_port_pair_list:
    list of ip port tuples to connect to the dht
    :param listen_port: port to listen on
    :return: instance of server
    """
    get_logger("kademlia")
    global _node_instance
    if _node_instance is None:
        _node_instance = connect_dht(bootstrap_ip_port_pair_list, listen_port)

    logger.debug("set up DHT: %s", str(bootstrap_ip_port_pair_list))
    return _node_instance


def connect_dht(
    bootstrap_ip_port_pair_list: List[Tuple[str, int]],
    listen_port: int,
) -> Server:
    """
    connects to the distributed hash table
    if no bootstrap ip port pair list is given, it starts a new dht
    :param bootstrap_ip_port_pair_list:
    list of ip port tuples to connect to the dht
    :param listen_port: port to listen on
    :return: instance of server
    """
    node = Server(storage=DropPeerDHTStorage(TRACKER_DROP_AVAILABILITY_TTL))
    node.listen(listen_port)
    loop = asyncio.get_event_loop()
    if len(bootstrap_ip_port_pair_list) > 0:
        loop.run_until_complete(node.bootstrap(bootstrap_ip_port_pair_list))

    # t1 = threading.Thread(target=dht_thread, args=(
    #     loop, node, listen_port,)
    # )
    # t1.start()

    return node


class DropPeerDHTStorage(IStorage):
    def __init__(self, ttl: int=TRACKER_DROP_AVAILABILITY_TTL) -> None:
        """
        Creates a new DropPeerDHTStorage module to plug into the dht
        :param ttl: ttl of entries in the dht
        """
        self.data = OrderedDict()  # type: OrderedDict[bytes, Any]
        self.ttl = ttl

    def __setitem__(self, key: bytes, value: Tuple[bytes, str, int]) -> None:
        self.cull_entry(key)
        if key in self.data:
            self.data[key] = self.data[key] + [
                (int(time.monotonic()), value),
            ]
        else:
            self.data[key] = [
                (int(time.monotonic()), value),
            ]
        logger.debug("Set new drop peer value to: %s", str(self.data[key]))

    def cull_entry(self, key: bytes) -> None:
        if key not in self.data:
            return
        old_data = self.data[key]
        new_data = []  # type: List[Tuple[bytes, str, int]]
        for entry in old_data:
            if (entry[0] + self.ttl > time.monotonic() and
                    entry[0] < time.monotonic()):
                new_data += entry

        self.data[key] = new_data

    def get(self, key: bytes, default=None) -> Any:
        if key in self.data:
            return self.__getitem__(key)
        return default

    def __getitem__(self, key: bytes) -> Any:
        if key in self.data:
            self.cull_entry(key)
            return self[key]
        raise KeyError("Key not found")

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return repr(self.data)

    def items(self):
        ikeys = self.data.keys()
        ivalues = map(lambda x: x[1], self.data.values())
        return zip(ikeys, ivalues)

    # def _tripleIterable(self):
        # ikeys = self.data.keys()
        # ibirthday = map(operator.itemgetter(0), self.data.values())
        # ivalues = map(operator.itemgetter(1), self.data.values())
        # return zip(ikeys, ibirthday, ivalues)

    def iteritemsOlderThan(self, secondsOld):
        """
        This method is unnesessary due to the setting method culling inputs
        and that the default ttl is less than 1 hour. The kademlia paper calls
        for refreshing entries are 1 hour old, but there are no entries older
        than 1 hour
        """
        # minBirthday = time.monotonic() - secondsOld
        # zipped = self._tripleIterable()
        # matches = takewhile(lambda r: minBirthday >= r[1], zipped)
        return []

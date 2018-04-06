import asyncio
import operator
import time
from collections import OrderedDict
from itertools import takewhile
from typing import List
from typing import Tuple

from kademlia import IStorage  # type: ignore
from kademlia import Server  # type: ignore

from syncr_backend.constants import TRACKER_DROP_AVAILABILITY_TTL


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

    return node


class DropPeerDHTStorage(IStorage):
    def __init__(self, ttl: int=TRACKER_DROP_AVAILABILITY_TTL) -> None:
        """
        By default, max age is a week.
        """
        self.data = OrderedDict()  # type: OrderedDict
        self.ttl = ttl

    def __setitem__(self, key: bytes, value: Tuple[bytes, str, int]) -> None:
        self.cull_entry(key)
        self.data[key] = self.data[key] + [
            (int(time.monotonic()), value),
        ]

    def cull_entry(self, key: bytes):
        if key not in self.data:
            return
        old_data = self.data[key]
        new_data = []  # type: List[Tuple[bytes, str, int]]
        for entry in old_data:
            if (entry[0] + self.ttl > time.monotonic() and
                    entry[0] < time.monotonic()):
                new_data += entry

        self.data[key] = new_data

    def get(self, key: bytes, default=None):
        if key in self.data:
            return self.__getitem__(key)
        return default

    def __getitem__(self, key: bytes):
        if key in self.data:
            self.data[key] = self.cull_entry(key)
            return self[key]
        raise Exception("Key not found")

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return repr(self.data)

    def _tripleIterable(self):
        ikeys = self.data.keys()
        ibirthday = map(operator.itemgetter(0), self.data.values())
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ibirthday, ivalues)

    def iteritemsOlderThan(self, secondsOld):
        minBirthday = time.monotonic() - secondsOld
        zipped = self._tripleIterable()
        matches = takewhile(lambda r: minBirthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

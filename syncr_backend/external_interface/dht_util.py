import asyncio
import pickle
from typing import Any
from typing import List
from typing import Tuple

from kademlia.network import Server  # type: ignore
from kademlia.storage import ForgetfulStorage  # type: ignore

from syncr_backend.util.log_util import get_logger


logger = get_logger(__name__)

_node_instance = None


def get_dht() -> Server:
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
    global _node_instance
    if _node_instance is None:
        raise TypeError("DHT has not been initilized")
    return _node_instance


def initialize_dht(
    bootstrap_ip_port_pair_list: List[Tuple[str, int]],
    listen_port: int,
) -> None:
    """
    connects to the distributed hash table
    if no bootstrap ip port pair list is given, it starts a new dht
    :param bootstrap_ip_port_pair_list:
    list of ip port tuples to connect to the dht
    :param listen_port: port to listen on
    :return: instance of server
    """
    global _node_instance

    get_logger("kademlia")

    logger.debug("set up DHT: %s", str(bootstrap_ip_port_pair_list))

    node = Server()
    node.listen(listen_port)
    loop = asyncio.get_event_loop()
    if len(bootstrap_ip_port_pair_list) > 0:
        loop.run_until_complete(node.bootstrap(bootstrap_ip_port_pair_list))

    # t1 = threading.Thread(target=dht_thread, args=(
    #     loop, node, listen_port,)
    # )
    # t1.start()

    _node_instance = node


class DropPeerDHTStorage(ForgetfulStorage):
    def __setitem__(self, key: Any, value: Any) -> None:

        if type(value) == frozenset and key in self.data:
            try:
                current_set = pickle.loads(self.data[key][1])
                if type(current_set) == frozenset:
                    new_value = pickle.dumps(current_set.union(value))
                    super().__setitem__(key, new_value)
                    return

            except pickle.UnpicklingError:
                print("Could not unpickle current data")

        super().__setitem__(key, value)

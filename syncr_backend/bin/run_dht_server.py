#!/usr/bin/env python
import argparse
import asyncio
from typing import List  # NOQA

from syncr_backend.external_interface.dht_util import initialize_dht


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "port",
        type=int,
        nargs=1,
        help="listenport of server",
    )
    parser.add_argument(
        "--bootstrap-peers",
        type=str,
        help=(
            'Peers of the DHT bootstrap.\n'
            'Usage: --bootstrap-peers ip:port,ip2:port2,...'
        ),
    )
    args = parser.parse_args()

    iplist = []  # type: List[str]
    portlist = []  # type: List[int]
    if args.bootstrap_peers is not None:
        peerlist = args.bootstrap_peers.split(',')
        try:
            iplist = list(map(lambda x: x.split(':')[0], peerlist))

            portlist = list(map(lambda x: int(x.split(':')[1]), peerlist))

        except IndexError:
            print("Must have at least 1 bootstrap ip")
            exit(1)

    bootstrap_list = list(zip(iplist, portlist))
    initialize_dht(bootstrap_list, args.port[0])
    loop = asyncio.get_event_loop()
    loop.run_forever()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
import argparse
import asyncio
import threading
import time
from typing import Any
from typing import List

from syncr_backend.external_interface.dht_util import initialize_dht
from syncr_backend.external_interface.drop_peer_store import send_drops_to_dps
from syncr_backend.init import drop_init
from syncr_backend.init import node_init
from syncr_backend.metadata.drop_metadata import send_my_pub_key
from syncr_backend.network.listen_requests import listen_requests
from syncr_backend.util import crypto_util
from syncr_backend.util import drop_util
from syncr_backend.util.fileio_util import load_config_file
from syncr_backend.util.log_util import get_logger
# from syncr_backend.network import send_requests
logger = get_logger(__name__)


def run_backend() -> None:
    """
    Runs the backend
    """
    input_args_parser = argparse.ArgumentParser()
    input_args_parser.add_argument(
        "ip",
        type=str,
        nargs=1,
        help='ip to bind listening server',
    )
    input_args_parser.add_argument(
        "port",
        type=str,
        nargs=1,
        help='port to bind listening server',
    )
    input_args_parser.add_argument(
        "--backendonly",
        action="store_true",
        help='runs only the backend if added as an option',
    )
    input_args_parser.add_argument(
        "--external_address",
        type=str,
        help="Set this if the external address is different from the listen "
        "address",
    )
    input_args_parser.add_argument(
        "--external_port",
        type=int,
        help="Set this if the external port is different from the listen port",
    )
    input_args_parser.add_argument(
        "--debug_commands",
        type=str,
        help="Command file to send debug commands",
    )
    arguments = input_args_parser.parse_args()
    if arguments.external_address is not None:
        ext_addr = arguments.external_address
    else:
        ext_addr = arguments.ip[0]
    if arguments.external_port is not None:
        ext_port = arguments.ext_port
    else:
        ext_port = int(arguments.port[0])

    loop = asyncio.get_event_loop()

    # initilize dht
    config_file = loop.run_until_complete(load_config_file())
    if config_file['type'] == 'dht':
        ip_port_list = list(
            zip(
                config_file['bootstrap_ips'],
                config_file['bootstrap_ports'],
            ),
        )
        initialize_dht(ip_port_list, config_file['listen_port'])

    loop.create_task(send_my_pub_key())

    shutdown_flag = threading.Event()
    request_listen_thread = threading.Thread(
        target=listen_requests,
        args=[
            arguments.ip[0], arguments.port[0], loop,
            shutdown_flag,
        ],
    )

    request_listen_thread.start()
    loop.create_task(send_drops_to_dps(ext_addr, ext_port, shutdown_flag))

    if not arguments.backendonly:
        if arguments.debug_commands is None:
            read_cmds_from_cmdline()
        else:
            run_debug_commands(arguments.debug_commands)
        shutdown_flag.set()
        loop = asyncio.get_event_loop()
        # network_util.close_socket_thread(
        #     arguments.ip[0], int(arguments.port[0]),
        # )
        loop.stop()
        request_listen_thread.join()


def run_debug_commands(commands_file: str) -> None:
    """
    Read and execute commands a list of semicolon separated commands as input
    :param commands: list of semicolon separated commands
    """
    with open(commands_file) as f:
        commands = f.read().replace('\n', '')

    commandlist = commands.split(';')
    for command in commandlist:

        args = command.split(' ')
        logger.info("Ran Command %s", args)
        execute_function(args[0], args[1:])


def read_cmds_from_cmdline() -> None:
    """
    Read and execute commands given as cmdline input
    """
    exit_flag = False
    while not exit_flag:
        command = input("5yncr >>> ").split(' ')
        return_list = ["", []]
        parse_cmd_thread = threading.Thread(
            target=parse_cmd,
            args=[command, return_list],
        )
        parse_cmd_thread.start()
        parse_cmd_thread.join()
        function_name = str(return_list[0])
        args = list(return_list[1])

        if function_name is None:
            continue
        if function_name != 'exit':
            execute_function(function_name, args)
        else:
            exit_flag = True


def parse_cmd(
    command: List[str],
    return_list: List[Any],
) -> None:
    """
    Parse command given in arguments
    :param command: str command to run
    :param return_list: for when calling in a thread, the return list is
    modified to be the return value of the function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "function",
        type=str,
        nargs=1,
        help="string name of the function to be ran",
    )

    parser.add_argument(
        "--args",
        type=str,
        nargs='*',
        help='arguments for the function to be ran',
    )
    args = parser.parse_args(args=command)
    return_list[0] = args.function[0]
    if args.args is not None:
        return_list[1] = args.args
    else:
        return_list[1] = []


def execute_function(function_name: str, args: List[str]) -> None:
    """
    Runs a function with the given args
    TODO: add real drop/metadata request commands that interface
    with the filesystem
    TODO: handle exceptions for real

    :param function_name: string name of the function to run
    :param args: arguments for the function to run
    """
    loop = asyncio.get_event_loop()
    # for functions that create or destroy the init directory
    if function_name == "node_init":
        node_init.initialize_node(*args)
    elif function_name == "node_force_init":
        node_init.force_initialize_node(*args)
    elif function_name == "delete_node":
        node_init.delete_node_directory(*args)

    # drop functions
    elif function_name == "drop_init":
        drop_init.initialize_drop(args[0])

    elif function_name == "drop_update":
        drop_id = crypto_util.b64decode(args[0].encode())
        task = loop.create_task(drop_util.update_drop(drop_id))
        while not task.done():
            time.sleep(10)

    elif function_name == "sync_drop":
        drop_id = crypto_util.b64decode(args[0].encode())
        # takes drop_id as b64 and save+directory

        async def sync_wrapper(drop_id: bytes, save_dir: str) -> None:

            await drop_util.sync_drop(drop_id, save_dir)

        task = loop.create_task(sync_wrapper(drop_id, args[1]))
        while not task.done():
            time.sleep(10)

    else:
        print("Function [%s] not found" % (function_name))


if __name__ == '__main__':
    run_backend()

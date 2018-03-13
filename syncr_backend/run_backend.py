#!/usr/bin/env python
import argparse
import sys
from typing import List
from typing import Tuple
import threading
from syncr_backend.init import drop_init
from syncr_backend.init import node_init
from syncr_backend.network.listen_requests import listen_requests
from syncr_backend.network import send_requests


def run_backend() -> None:
    """
    Runs the backend
    """
    request_listen_thread = threading.Thread(target=listen_requests, args=[])
    request_listen_thread.start()


def read_cmds_from_cmdline() -> None:
    """
    Read and execute commands given as cmdline input
    """
    exit = False
    while not exit:
        command = input("5yncr >>> ")
        function_name, args = parse_cmd(command)
        if function_name != 'exit':
            execute_function(function_name, args)
        else:
            exit = True


def parse_cmd(command: str) -> Tuple[str, List[str]]:
    """
    Parse command given in arguments
    :param command: str command to run
    :return: Tuple of function name and argumen
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
    if args.args is not None:
        return (args.function[0], args.args)
    else:
        return (args.function[0], [])


def execute_function(function_name: str, args: List[str]):
    """
    Runs a function with the given args
    TODO: add real drop/metadata request commands that interface
    with the filesystem

    :param function_name: string name of the function to run
    :param args: arguments for the function to run
    """

    # for functions that create or destroy the init directory
    if function_name == "node_init":
        node_init.initialize_node(*args)
    elif function_name == "node_force_init":
        node_init.force_initialize_node(*args)
    elif function_name == "delete_node":
        node_init.delete_node_directory(*args)

    # drop functions
    if function_name == "drop_init":
        drop_init.initialize_drop(*args)

    # request functions, only for debug
    try:
        if function_name == "send_drop_metadata_request":
            print(send_requests.send_drop_metadata_request(*args))
        elif function_name == "send_file_metadata_request":
            print(send_requests.send_file_metadata_request(*args))
        elif function_name == "send_chunk_list_request":
            send_requests.send_chunk_list_request(*args)
        elif function_name == "send_chunk_request":
            send_requests.send_chunk_request(*args)
    # placeholder only for debugging
    except Exception:
        print("Error in handling request function")
        print(str(sys.exc_info()))


if __name__ == '__main__':
    run_backend()

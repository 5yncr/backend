import argparse
from typing import List

from syncr_backend import node_init


def execute_node_function(function_name: str, args: List[str]) -> None:
    """
    Runs a function with the given args

    :param function_name: string name of the function to run
    :param args: arguments for the function to run
    """
    function_map = {
        "node_init": node_init.initialize_node,
        "node_force_init": node_init.force_initialize_node,
    }
    output = function_map[function_name[0]](*args)
    print(output)


parser = argparse.ArgumentParser()
parser.add_argument(
    "function",
    type=str,
    nargs=1,
    help="string name of the function to be ran",
)

parser.add_argument(
    "function_args",
    type=str,
    nargs='?',
    help='arguments for the function to be ran',
)
args = parser.parse_args()
if args.function_args is not None:
    execute_node_function(args.function, args.function_args)
else:
    execute_node_function(args.function, [])

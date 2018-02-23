import os
import shutil

from syncr_backend import crypto_util


def force_initialize_node() -> None:
    """Initialize new node in .node directory
    and overwrite existing .node dir"""

    if os.path.exists(".node"):
        shutil.rmtree(".node")

    initialize_node()


def is_node_initialized() -> bool:
    return os.path.exists(".node")


def initialize_node() -> None:
    """Initialize new node in .node directory
    Create the private key file"""
    try:
        if os.path.exists(".node"):
            raise FileExistsError

        os.mkdir(".node")
        private_key = crypto_util.generate_private_key()
        write_private_key_to_disk(private_key)

    except (FileExistsError):
        print("Error: node already initiated")


def write_private_key_to_disk(key: crypto_util.rsa.RSAPrivateKey) -> None:
    """Write Private Key (and public key attached) to file"""
    try:
        if os.path.exists(".node/private_key.pem"):
            raise FileExistsError

        with open(".node/private_key.pem", "wb") as keyfile:
            keyfile.write(crypto_util.dump_private_key(key))
            keyfile.close()
    except (FileNotFoundError):
        print("Error: File could not be opened")
    except (FileExistsError):
        print("Error: File already exists")


def load_private_key_from_disk() -> crypto_util.rsa.RSAPrivateKey:
    """Load Private Key (and public key) from file"""
    try:

        with open(".node/private_key.pem", "rb") as keyfile:
            return crypto_util.load_private_key(keyfile.read())

    except (FileNotFoundError):
        print("Error: File could not be opened")

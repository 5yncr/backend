import os

from syncr_backend import crypto_util
from syncr_backend import drop_metadata
from syncr_backend import node_init


def initialize_drop(directory: str) -> None:
    start = os.getcwd()
    os.chdir(directory)
    priv_key = node_init.load_private_key_from_disk()
    node_id = crypto_util.node_id_from_public_key(priv_key.public_key())
    (drop_m, files_m) = drop_metadata.make_drop_metadata(
        path=directory,
        drop_name=os.path.basename(directory),
        owner=node_id,
    )
    drop_m.write_file()
    for f_m in files_m.values():
        f_m.write_file()
    os.chdir(start)

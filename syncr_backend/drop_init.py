import os

from syncr_backend import crypto_util
from syncr_backend import drop_metadata
from syncr_backend import node_init
from syncr_backend.constants import DEFAULT_DROP_METADATA_LOCATION
from syncr_backend.constants import DEFAULT_FILE_METADATA_LOCATION


def initialize_drop(directory: str) -> None:
    os.chdir(directory)
    priv_key = node_init.load_private_key_from_disk()
    node_id = crypto_util.node_id_from_public_key(priv_key.public_key())
    (drop_m, files_m) = drop_metadata.make_drop_metadata(
        path=directory,
        drop_name=os.path.basename(directory),
        owner=node_id,
    )
    drop_m.write_file(
        os.path.join(directory, DEFAULT_DROP_METADATA_LOCATION),
    )
    for f_m in files_m.values():
        f_m.write_file(
            os.path.join(directory, DEFAULT_FILE_METADATA_LOCATION),
        )

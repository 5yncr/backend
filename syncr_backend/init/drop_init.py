import os
from typing import Dict
from typing import List
from typing import Optional  # noqa
from typing import Set
from typing import Tuple

from syncr_backend.constants import DEFAULT_DROP_METADATA_LOCATION
from syncr_backend.constants import DEFAULT_FILE_METADATA_LOCATION
from syncr_backend.constants import DEFAULT_METADATA_LOOKUP_LOCATION
from syncr_backend.init import node_init
from syncr_backend.metadata import drop_metadata
from syncr_backend.metadata import file_metadata
from syncr_backend.metadata.drop_metadata import DropMetadata
from syncr_backend.metadata.file_metadata import FileMetadata
from syncr_backend.network import send_requests
from syncr_backend.util import crypto_util
from syncr_backend.util import fileio_util


def initialize_drop(directory: str) -> None:
    """Initialize a drop from a directory. Generates the necesssary drop and
    file metadata files and writes the drop location to the central config dif

    :param directory: The directory to initialize a drop from
    """
    priv_key = node_init.load_private_key_from_disk()
    node_id = crypto_util.node_id_from_public_key(priv_key.public_key())
    (drop_m, files_m) = make_drop_metadata(
        path=directory,
        drop_name=os.path.basename(directory),
        owner=node_id,
    )
    drop_m.write_file(
        is_latest=True,
        metadata_location=os.path.join(
            directory, DEFAULT_DROP_METADATA_LOCATION,
        ),
    )
    for f_m in files_m.values():
        f_m.write_file(
            os.path.join(directory, DEFAULT_FILE_METADATA_LOCATION),
        )
    save_drop_location(drop_m.id, directory)


def save_drop_location(drop_id: bytes, location: str) -> None:
    """Save a drops location in the central data dir

    :param drop_id: The unencoded drop id
    :param location: Where the drop is located on disk
    """
    save_path = _get_save_path()

    encoded_drop_id = crypto_util.b64encode(drop_id).decode('utf-8')

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    with open(os.path.join(save_path, encoded_drop_id), 'w') as f:
        f.write(location)


def get_drop_location(drop_id: bytes) -> str:
    """Get a drops location on disk, from the drop id

    :param drop_id: The unencoded drop id
    :return: The directory the drop is in
    """
    save_path = _get_save_path()

    encoded_drop_id = crypto_util.b64encode(drop_id).decode('utf-8')

    with open(os.path.join(save_path, encoded_drop_id), 'r') as f:
        return f.read()


def add_drop_from_id(drop_id: bytes, save_dir: str) -> None:
    """Given a drop_id and save directory, sets up the directory for syncing
    and adds the info to the global dir

    Should be followed by calls to `get_drop_metadata`, `get_file_metadata` for
    each file, and `sync_drop_contents`

    :param drop_id: The drop id to add
    :save_dir: where to download the drop to
    """

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    os.mkdir(os.path.join(save_dir, DEFAULT_DROP_METADATA_LOCATION))
    save_drop_location(drop_id, save_dir)


def get_drop_metadata(
    drop_id: bytes, save_dir: str, peers: List[Tuple[str, int]],
) -> DropMetadata:
    metadata_dir = os.path.join(save_dir, DEFAULT_DROP_METADATA_LOCATION)
    metadata = DropMetadata.read_file(drop_id, metadata_dir)

    if metadata is None:
        metadata = send_requests.do_request(
            request_fun=send_requests.send_drop_metadata_request,
            peers=peers,
            fun_args={'drop_id': drop_id},
        )

        metadata.write_file(is_latest=True, metadata_location=metadata_dir)

    return metadata


def get_file_metadata(
    drop_id: bytes, file_id: bytes, save_dir: str,
    peers: List[Tuple[str, int]],
) -> FileMetadata:
    metadata_dir = os.path.join(save_dir, DEFAULT_FILE_METADATA_LOCATION)
    metadata = FileMetadata.read_file(file_id, metadata_dir)
    if metadata is None:
        metadata = send_requests.do_request(
            request_fun=send_requests.send_file_metadata_request,
            peers=peers,
            fun_args={'drop_id': drop_id, 'file_id': file_id},
        )

        metadata.write_file(metadata_dir)

    return metadata


def sync_drop_contents(
    drop_id: bytes, file_id: bytes, save_dir: str,
    peers: List[Tuple[str, int]],
) -> Set[int]:
    file_metadata = get_file_metadata(drop_id, file_id, save_dir, peers)
    drop_metadata = get_drop_metadata(drop_id, save_dir, peers)
    file_name = drop_metadata.get_file_name_from_id(file_metadata.file_id)
    full_path = os.path.join(save_dir, file_name)

    fileio_util.create_file(full_path, file_metadata.file_length)

    for ip, port in peers:
        needed_chunks = file_metadata.needed_chunks
        avail_chunks = send_requests.send_chunk_list_request(
            ip=ip,
            port=port,
            drop_id=drop_id,
            file_id=file_id,
        )
        avail_set = set(avail_chunks)
        can_get_from_peer = avail_set - needed_chunks
        if not can_get_from_peer:
            continue
        for cid in can_get_from_peer:
            chunk = send_requests.send_chunk_request(
                ip=ip,
                port=port,
                drop_id=drop_id,
                file_id=file_id,
                file_index=cid,
            )
            try:
                fileio_util.write_chunk(
                    filepath=full_path,
                    position=cid,
                    contents=chunk,
                    chunk_hash=file_metadata.hashes[cid],
                )
                file_metadata.finish_chunk(cid)
                needed_chunks -= {cid}
            except crypto_util.VerificationException:
                break

    return needed_chunks


def make_drop_metadata(
    path: str,
    drop_name: str,
    owner: bytes,
    other_owners: Dict[bytes, int]={},
    ignore: List[str]=[],
) -> Tuple[DropMetadata, Dict[str, FileMetadata]]:
    """Makes drop metadata and file metadatas from a directory

    :param path: The directory to make metadata from
    :param name: The name of the drop to create
    :param drop_id: The drop id of the drop metadata, must match the owner
    :param owner: The owner, must match the drop id
    :param other_owners: Other owners, may be empty
    :return: A tuple of the drop metadata, and a dict from file names to file
    metadata
    """
    drop_id = drop_metadata.gen_drop_id(owner)
    files = {}
    for (dirpath, filename) in fileio_util.walk_with_ignore(path, ignore):
        full_name = os.path.join(dirpath, filename)
        files[full_name] = file_metadata.make_file_metadata(full_name, drop_id)

    file_hashes = {
        os.path.relpath(name, path): m.file_id for (name, m) in files.items()
    }
    dm = DropMetadata(
        drop_id=drop_id,
        name=drop_name,
        version=drop_metadata.DropVersion(1, crypto_util.random_int()),
        previous_versions=[],
        primary_owner=owner,
        other_owners=other_owners,
        signed_by=owner,
        files=file_hashes,
    )

    return (dm, files)


def _get_save_path() -> str:
    node_info_path = node_init.get_full_init_directory()
    save_path = os.path.join(node_info_path, DEFAULT_METADATA_LOOKUP_LOCATION)
    return save_path

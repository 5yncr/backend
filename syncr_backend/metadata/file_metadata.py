import hashlib
import os
from math import ceil
from typing import BinaryIO
from typing import List
from typing import Optional
from typing import Set  # noqa

import bencode  # type: ignore

from syncr_backend.constants import DEFAULT_CHUNK_SIZE
from syncr_backend.constants import DEFAULT_DROP_METADATA_LOCATION
from syncr_backend.init import drop_init
from syncr_backend.metadata.drop_metadata import DropMetadata
from syncr_backend.util import crypto_util
from syncr_backend.util import fileio_util


class FileMetadata(object):

    # TODO: define PROTOCOL_VERSION somewhere
    def __init__(
        self, hashes: List[bytes], file_hash: bytes, file_length: int,
        drop_id: bytes,
        chunk_size: int=DEFAULT_CHUNK_SIZE, protocol_version: int=1,
    ) -> None:
        self.hashes = hashes
        self.file_hash = file_hash
        self.file_length = file_length
        self.chunk_size = chunk_size
        self._protocol_version = protocol_version
        self._downloaded_chunks = None  # type: Optional[Set[int]]
        self.num_chunks = ceil(file_length / chunk_size)
        self.drop_id = drop_id
        self._save_dir = None  # type: Optional[str]

    def encode(self) -> bytes:
        """Make the bencoded file that will be transfered on the wire

        :return: bytes that is the file
        """
        d = {
            "protocol_version": self._protocol_version,
            "chunk_size": self.chunk_size,
            "file_length": self.file_length,
            "file_hash": self.file_hash,
            "chunks": self.hashes,
            "drop_id": self.drop_id,
        }
        return bencode.encode(d)

    def write_file(
        self, metadata_location: str,
    ) -> None:
        """Write this file metadata to a file

        :param metadata_location: where to save it
        """
        file_name = crypto_util.b64encode(self.file_hash).decode("utf-8")
        if not os.path.exists(metadata_location):
            os.makedirs(metadata_location)
        with open(os.path.join(metadata_location, file_name), 'wb') as f:
            f.write(self.encode())

    @staticmethod
    def read_file(
        file_hash: bytes,
        metadata_location: str,
    ) -> Optional['FileMetadata']:
        """Read a file metadata file and return FileMetadata

        :param file_hash: The hash of the file to read
        :return: a FileMetadata object or None if it does not exist
        """
        file_name = crypto_util.b64encode(file_hash).decode("utf-8")
        if not os.path.exists(os.path.join(metadata_location, file_name)):
            return None

        with open(os.path.join(metadata_location, file_name), 'rb') as f:
            b = b''
            while True:
                data = f.read(65536)
                if not data:
                    break
                b += data
            return FileMetadata.decode(b)

    @staticmethod
    def decode(data: bytes) -> 'FileMetadata':
        """Decode a bencoded byte array into a FileMetadata object

        :param data: bencoded byte array of file metadata
        :return: FileMetadata object
        """
        d = bencode.decode(data)
        return FileMetadata(
            hashes=d['chunks'], file_hash=d['file_hash'],
            file_length=d['file_length'], chunk_size=d['chunk_size'],
            drop_id=d['drop_id'],
            protocol_version=d['protocol_version'],
        )

    @property
    def save_dir(self) -> str:
        if self._save_dir is None:
            self._save_dir = drop_init.get_drop_location(self.drop_id)
        return self._save_dir

    def _calculate_downloaded_chunks(self) -> Set[int]:
        dm = DropMetadata.read_file(
            id=self.drop_id,
            metadata_location=os.path.join(
                self.save_dir, DEFAULT_DROP_METADATA_LOCATION,
            ),
        )
        if dm is None:
            return set()
        file_name = dm.get_file_name_from_id(self.file_hash)
        full_name = os.path.join(self.save_dir, file_name)
        downloaded_chunks = set()  # type: Set[int]
        for chunk_idx in range(self.num_chunks):
            _, h = fileio_util.read_chunk(
                filepath=full_name,
                position=chunk_idx,
                file_hash=self.hashes[chunk_idx],
                chunk_size=self.chunk_size,
            )
            if h == self.hashes[chunk_idx]:
                downloaded_chunks.add(chunk_idx)
        return downloaded_chunks

    @property
    def downloaded_chunks(self) -> Set[int]:
        if self._downloaded_chunks is None:
            self._downloaded_chunks = self._calculate_downloaded_chunks()
        return self._downloaded_chunks

    @property
    def needed_chunks(self) -> Set[int]:
        all_chunks = {x for x in range(self.num_chunks)}
        return all_chunks - self.downloaded_chunks

    def finish_chunk(self, chunk_id: int) -> None:
        self.downloaded_chunks.add(chunk_id)


def file_hashes(
    f: BinaryIO, chunk_size: int=DEFAULT_CHUNK_SIZE,
) -> List[bytes]:
    """Given an open file in mode 'rb', hash its chunks and return a list of
    the hashes

    :param f: open file
    :param chunk_size: the chunk size to use, probably don't change this
    :return: list of hashes
    """
    hashes = []

    b = f.read(chunk_size)
    while len(b) > 0:
        hashes.append(crypto_util.hash(b))

        b = f.read(chunk_size)

    return hashes


def hash_file(f: BinaryIO) -> bytes:
    """Hash a file

    :param f: An open file, seeked to 0
    :return: The hash bytes
    """
    sha = hashlib.sha256()
    while True:
        data = f.read(65536)
        if not data:
            break
        sha.update(data)
    return sha.digest()


def make_file_metadata(filename: str, drop_id: bytes) -> FileMetadata:
    """Given a file name, return a FileMetadata object

    :param filename: The name of the file to open and read
    :return: FileMetadata object
    """
    f = open(filename, 'rb')
    size = os.path.getsize(f.name)

    hashes = file_hashes(f)
    f.seek(0)
    file_hash = hash_file(f)

    f.close()

    return FileMetadata(hashes, file_hash, size, drop_id)

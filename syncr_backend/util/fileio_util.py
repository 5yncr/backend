"""Helper functions for reading from and writing to the filesystem"""
import fnmatch
import os
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from syncr_backend.constants import DEFAULT_CHUNK_SIZE
from syncr_backend.constants import DEFAULT_IGNORE
from syncr_backend.constants import DEFAULT_INCOMPLETE_EXT
from syncr_backend.util import crypto_util
from syncr_backend.util.crypto_util import Chunk
from syncr_backend.util.crypto_util import ChunkID
from syncr_backend.util.crypto_util import H
from syncr_backend.util.log_util import get_logger


logger = get_logger(__name__)


def write_chunk(
    filepath: str, position: int, contents: Chunk, chunk_hash: ChunkID,
    chunk_size: int=DEFAULT_CHUNK_SIZE,
) -> None:
    """Takes a filepath, position, contents, and contents hash and writes it to
    a file correctly.  Assumes the file has been created.  Will check the hash,
    and raise a VerificationException if the provided chunk_hash doesn't match.
    May raise relevant IO exceptions.

    If the file extension indicates the file is complete, does nothing.

    :param filepath: the path of the file to write to
    :param position: the posiiton in the file to write to
    :param contents: the contents to write
    :param chunk_hash: the expected hash of contents
    :param chunk_size: (optional) override the chunk size, used to calculate
    the position in the file
    :return: None
    """
    if is_complete(filepath):
        logger.info("file %s already done, not writing", filepath)
        return

    filepath += DEFAULT_INCOMPLETE_EXT
    if H.hash(contents).val != chunk_hash.val:
        raise crypto_util.VerificationException()
    logger.debug("writing chunk with hash %s", chunk_hash)

    with open(filepath, 'wb') as f:
        pos_bytes = position * chunk_size
        f.seek(pos_bytes)
        f.write(contents)


def read_chunk(
    filepath: str, position: int, file_hash: Optional[ChunkID]=None,
    chunk_size: int=DEFAULT_CHUNK_SIZE,
) -> Tuple[Chunk, ChunkID]:
    """Reads a chunk for a file, returning the contents and its hash.  May
    raise relevant IO exceptions

    If file_hash is provided, will check the chunk that is read

    :param filepath: the path of the file to read from
    :param position: where to read from
    :param file_hash: if provided, will check the file hash
    :param chunk_size: (optional) override the chunk size
    :return: a double of (contents, hash), both bytes
    """
    if not is_complete(filepath):
        logger.debug("file %s not done, adding extention", filepath)
        filepath += DEFAULT_INCOMPLETE_EXT

    with open(filepath, 'rb') as f:
        pos_bytes = position * chunk_size
        data = crypto_util.read_chunk(f, pos_bytes, chunk_size)

    h = H.hash(data)
    if file_hash is not None:
        logger.info("input file_hash is not None, checking")
        if h.val != file_hash.val:
            raise crypto_util.VerificationException()
    return (data, h)


def create_file(
    filepath: str, size_bytes: int,
) -> None:
    """Create a file at filepath of the correct size. May raise relevant IO
    exceptions

    If filepath exists, calling this indicates there are updates, and filepath
    gets moved to filepath + incomplete_ext

    :param filepath: where to create the file
    :param size: the size to allocate
    :return: None
    """
    new_path = filepath + DEFAULT_INCOMPLETE_EXT
    try:
        if is_complete(filepath):
            logger.info("file %s is done, moving it to be not done", filepath)
            os.replace(filepath, new_path)
    except FileNotFoundError:
        pass

    filepath = new_path
    with open(filepath, 'wb') as f:
        logger.debug("truncating %s ot %s bytes", filepath, size_bytes)
        f.truncate(size_bytes)


def mark_file_complete(filepath: str) -> None:
    """Marks a file as completed by renaming it to remove the
    DEFAULT_INCOMPLETE_EXT

    May fail on some systems if the destination exists

    :param filepath: The path of the file, without the extension
    :return: None
    """
    logger.debug("marking %s done", filepath)
    old_file = filepath + DEFAULT_INCOMPLETE_EXT
    os.rename(old_file, filepath)


def is_complete(filepath: str) -> bool:
    """Tests if file is complete, based on its extension

    True if filepath exists, False if filepath + incomplete_ext exists
    Raises FileNotFoundError if neither exists

    :param filepath: The path to check for completion
    :return: Whether the file is downloaded, based on its extension
    """
    unfinished_path = filepath + DEFAULT_INCOMPLETE_EXT
    if os.path.isfile(unfinished_path):
        logger.debug("file %s is not done", unfinished_path)
        return False
    if os.path.isfile(filepath):
        logger.debug("file %s is done", filepath)
        return True
    logger.error("file %s not found", filepath)
    raise FileNotFoundError(filepath)


def walk_with_ignore(
    path: str, ignore: List[str],
) -> Iterator[Tuple[str, str]]:
    """Walks the files in a directory, while filtering anything that should be
    ignored.  Implemented on top of os.walk, but instead returns an iterator
    over (dirpath, filename)

    :param path: The path to walk
    :param ignore: Patterns to ignore
    :return: An iterator of (dirpath, filename) that are in path but not ignore
    """
    ignore += DEFAULT_IGNORE
    for (dirpath, _, filenames) in os.walk(path):
        if any([fnmatch.fnmatch(dirpath, i) for i in ignore]):
            continue
        for name in filenames:
            if any([fnmatch.fnmatch(name, i) for i in ignore]):
                continue
            full_name = os.path.join(dirpath, name)
            if any([fnmatch.fnmatch(full_name, i) for i in ignore]):
                continue
            yield (dirpath, name)

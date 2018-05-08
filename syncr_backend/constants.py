"""Constants"""
import os
from enum import Enum
from enum import IntEnum


NODE_ID_BYTE_SIZE = 32  #: Size of a node id in bytes
DROP_ID_BYTE_SIZE = 64  #: Size of a drop id in bytes


class TrackerRequest(IntEnum):
    """Tracker request types"""
    GET_KEY = 0  #: Get a key
    POST_KEY = 1  #: Add a key
    GET_PEERS = 2  #: Geet peers
    POST_PEER = 3  #: Add a peer

    def __str__(self) -> str:
        return str(self.name)


# Tuple structure for drop availability
# TODO: make a NamedTuple
TRACKER_DROP_NODE_INDEX = 0
TRACKER_DROP_IP_INDEX = 1
TRACKER_DROP_PORT_INDEX = 2
TRACKER_DROP_TIMESTAMP_INDEX = 3

#: TTL for drops in the DPS.  Also used for other TTLs throughout the code
TRACKER_DROP_AVAILABILITY_TTL = 300
# Tracker server result responses
TRACKER_OK_RESULT = 'OK'  #: OK text response from tracker
TRACKER_ERROR_RESULT = 'ERROR'  #: Error text response from tracker

# Node init constants
#: Default dir in ~/ to add node info to and location in a drop for metadata
DEFAULT_INIT_DIR = ".5yncr"
#: Location of pub keys in node init dir
DEFAULT_PUB_KEY_LOOKUP_LOCATION = "pub_keys"
#: PKS config file name (in init dir)
DEFAULT_PKS_CONFIG_FILE = "PublicKeyStore.config"
#: DPS config file name (in init dir)
DEFAULT_DPS_CONFIG_FILE = "DropPeerStore.config"
#: Location of metadata lookup dir (in init dir)
DEFAULT_METADATA_LOOKUP_LOCATION = "drops"

# file_metadata constants
DEFAULT_CHUNK_SIZE = 2**23  #: Default chunk size. Don't change this
#: directory of file metadata files in the drop
DEFAULT_FILE_METADATA_LOCATION = os.path.join(DEFAULT_INIT_DIR, "files")
#: directory of drop metadata files in the drop
DEFAULT_DROP_METADATA_LOCATION = os.path.join(DEFAULT_INIT_DIR, "drop")
#: filename of timestamp file that detects updates
DEFAULT_TIMESTAMP_LOCATION = os.path.join(DEFAULT_INIT_DIR, "timestamp")

#: Default set of files/folders to ignore when creating/updating a drop
DEFAULT_IGNORE = [DEFAULT_INIT_DIR]

# File constants
DEFAULT_INCOMPLETE_EXT = ".part"  #: Extension to add to incomplete files

# Request types
# TODO: make an enum
REQUEST_TYPE_DROP_METADATA = 1
REQUEST_TYPE_FILE_METADATA = 2
REQUEST_TYPE_CHUNK_LIST = 3
REQUEST_TYPE_CHUNK = 4
REQUEST_TYPE_NEW_DROP_METADATA = 5

#: The protocol version; not currently well used
PROTOCOL_VERSION = 1

# Errnos
# TODO: make an enum
ERR_NEXIST = 0
ERR_INCOMPAT = 1
ERR_INVINPUT = 2
ERR_EXCEPTION = 3

# Concurrency
#: Maximum number of files to download at once
MAX_CONCURRENT_FILE_DOWNLOADS = 4
#: Maximum number of chunks to download from a peer before trying another
MAX_CHUNKS_PER_PEER = 8
#: Maximum number of chunks to download at a time per file
MAX_CONCURRENT_CHUNK_DOWNLOADS = 8


class StrEnum(str, Enum):
    pass


# Frontend action types
# TODO: make an enum
class FrontendAction(StrEnum):
    """Frontend action strings"""
    GET_OWNED_SUBSCRIBED_DROPS = 'get_owned_subscribed_drops'
    GET_SELECTED_DROP = 'get_selected_drop'
    INITIALIZE_DROP = 'initialize_drop'
    INPUT_DROP_TO_SUBSCRIBE_TO = 'input_drop_to_subscribe'
    ADD_OWNER = 'add_owner'
    REMOVE_OWNER = 'remove_owner'
    DELETE_DROP = 'delete_drop'
    UNSUBSCRIBE = 'unsubscribe'
    NEW_VERSION = 'new_version'
    PENDING_CHANGES = 'get_pending_changes'
    SYNC_UPDATE = 'sync_update'
    SHARE_DROP = 'share_drop'
    GET_PENDING_CHANGES = 'get_pending_changes'
    GET_PUBLIC_KEY = 'get_public_key'

    def __str__(self) -> str:
        return(self.value)


# Frontend connection settings
#: TCP address for frontend communication
FRONTEND_TCP_ADDRESS = ('localhost', 12345)
#: UNIX address for frontend communication
FRONTEND_UNIX_ADDRESS = "unix_socket"

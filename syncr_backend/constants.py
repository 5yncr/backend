"""Constants!"""
import os


NODE_ID_BYTE_SIZE = 32
DROP_ID_BYTE_SIZE = 64

# Request types for tracker
TRACKER_REQUEST_GET_KEY = 0
TRACKER_REQUEST_POST_KEY = 1
TRACKER_REQUEST_GET_PEERS = 2
TRACKER_REQUEST_POST_PEER = 3

# Tuple structure for drop availability
TRACKER_DROP_NODE_INDEX = 0
TRACKER_DROP_IP_INDEX = 1
TRACKER_DROP_PORT_INDEX = 2
TRACKER_DROP_TIMESTAMP_INDEX = 3

# Tracker drop availability time to live
TRACKER_DROP_AVAILABILITY_TTL = 300

# Tracker server result responses
TRACKER_OK_RESULT = 'OK'
TRACKER_ERROR_RESULT = 'ERROR'

# Node init constants
DEFAULT_INIT_DIR = ".5yncr"
DEFAULT_PUB_KEY_LOOKUP_LOCATION = "pub_keys"
DEFAULT_PKS_CONFIG_FILE = "PublicKeyStore.config"
DEFAULT_DPS_CONFIG_FILE = "DropPeerStore.config"
DEFAULT_METADATA_LOOKUP_LOCATION = "drops"

# file_metadata constants
DEFAULT_CHUNK_SIZE = 2**23
DEFAULT_FILE_METADATA_LOCATION = os.path.join(DEFAULT_INIT_DIR, "files")
DEFAULT_DROP_METADATA_LOCATION = os.path.join(DEFAULT_INIT_DIR, "drop")

DEFAULT_IGNORE = [DEFAULT_INIT_DIR]

# File constants
DEFAULT_INCOMPLETE_EXT = ".part"

# Request types
REQUEST_TYPE_DROP_METADATA = 1
REQUEST_TYPE_FILE_METADATA = 2
REQUEST_TYPE_CHUNK_LIST = 3
REQUEST_TYPE_CHUNK = 4
REQUEST_TYPE_NEW_DROP_METADATA = 5

PROTOCOL_VERSION = 1

# Errnos
ERR_NEXIST = 0
ERR_INCOMPAT = 1
ERR_INVINPUT = 2
ERR_EXCEPTION = 3

# Concurrency
MAX_CONCURRENT_FILE_DOWNLOADS = 4
MAX_CHUNKS_PER_PEER = 8
MAX_CONCURRENT_CHUNK_DOWNLOADS = 8


# Frontend action types
ACTION_GET_OWNED_SUBSCRIBED_DROPS = 'get_owned_subscribed_drops'
ACTION_GET_SELECT_DROPS = 'get_selected_drop'
ACTION_INITIALIZE_DROP = 'initialize_drop'
ACTION_INPUT_DROP_TO_SUBSCRIBE_TO = 'input_drop_to_subscribe'
ACTION_SHARE_DROP = 'share_drop'
ACTION_ADD_OWNER = 'add_owner'
ACTION_REMOVE_OWNER = 'remove_owner'
ACTION_DELETE_DROP = 'delete_drop'
ACTION_UNSUBSCRIBE = 'unsubscribe'

# Frontend connection settings
FRONTEND_TCP_ADDRESS = ('localhost', 12345)
FRONTEND_UNIX_ADDRESS = "unix_socket"

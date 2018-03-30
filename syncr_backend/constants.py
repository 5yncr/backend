"""Constants!"""
import os


NODE_ID_BYTE_SIZE = 32
DROP_ID_BYTE_SIZE = 64

DEFAULT_BUFFER_SIZE = 4096

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
REQUEST_TYPE_FRONTEND_MESSAGE = 6

PROTOCOL_VERSION = 1

# Errnos
ERR_NEXIST = 0
ERR_INCOMPAT = 1

# Frontend action types
ACTION_REMOVE_FILE = 'r_f'
ACTION_GET_OWNED_DROPS = 'g_o_d'
ACTION_GET_SUB_DROPS = 'g_sub_d'
ACTION_GET_SELECT_DROPS = 'g_sel_d'
ACTION_GET_CONFLICTING_FILES = 'g_c_f'
ACTION_INPUT_NAME = 'i_n'
ACTION_INPUT_DROP_TO_SUBSCRIBE_TO = 'i_d_t_s'
ACTION_DECLINE_CONFLICT_FILE = 'd_c_f'
ACTION_ACCEPT_CONFLICT_FILE = 'a_c_f'
ACTION_ACCEPT_CHANGES = 'a_c'
ACTION_DECLINE_CHANGES = 'd_c'
ACTION_VIEW_CONFLICTS = 'v_c'
ACTION_ADD_FILE = 'a_f'
ACTION_SHARE_DROP = 's_d'
ACTION_VIEW_PENDING_CHANGES = 'v_p_c'
ACTION_ADD_OWNER = 'a_o'
ACTION_REMOVE_OWNER = 'r_o'
ACTION_DELETE_DROP = 'd_d'
ACTION_UNSUBSCRIBE = 'unsub'
ACTION_REQUEST_CHANGE = 'r_c'

NODE_ID_BYTE_SIZE = 32
DROP_ID_BYTE_SIZE = 64

# Request structure indices for Tracker
TYPE_INDEX = 0
ID_INDEX = 1
VALUE_INDEX = 2

# Tuple structure for drop availability
DROP_NODE_INDEX = 0
DROP_IP_INDEX = 1
DROP_PORT_INDEX = 2
DROP_TIMESTAMP_INDEX = 3

# Tracker drop availability time to live
DROP_AVAILABILITY_TTL = 5

# Tracker server result responses
OK_RESULT = 'OK'
ERROR_RESULT = 'ERROR'

# file_metadata constants
DEFAULT_CHUNK_SIZE = 2**23
DEFAULT_FILE_METADATA_LOCATION = b".files/"

# Node init constants
DEFAULT_INIT_DIR = ".node/"

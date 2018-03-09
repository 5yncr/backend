import socket
import sys
from socket import SHUT_RD

import bencode  # type: ignore

from syncr_backend.constants import DEFAULT_BUFFER_SIZE
from syncr_backend.constants import REQUEST_TYPE_CHUNK
from syncr_backend.constants import REQUEST_TYPE_CHUNK_LIST
from syncr_backend.constants import REQUEST_TYPE_DROP_METADATA
from syncr_backend.constants import REQUEST_TYPE_FILE_METADATA
from syncr_backend.constants import REQUEST_TYPE_NEW_DROP_METADATA
from syncr_backend.drop_init import get_drop_location
from syncr_backend.drop_metadata import DropMetadata
from syncr_backend.drop_metadata import DropVersion
from syncr_backend.network_util import send_response


def request_dispatcher(request: dict, conn: socket.socket) -> None:
    """

    :param request: dict containing request data
    :param conn: socket.accept() connection
    :return: None
    """
    function_map = {
        REQUEST_TYPE_DROP_METADATA: handle_request_drop_metadata,
        REQUEST_TYPE_FILE_METADATA: handle_request_file_metadata,
        REQUEST_TYPE_CHUNK_LIST: handle_request_chunk_list,
        REQUEST_TYPE_CHUNK: handle_request_chunk,
        REQUEST_TYPE_NEW_DROP_METADATA: handle_request_new_drop_metadata,
    }
    type = request['request_type']
    handle_function = function_map[type]

    handle_function(request, conn)


def handle_request_drop_metadata(request: dict, conn: socket.socket) -> None:
    """

    :param request:
    {
    "protocol_version": int,
    "request_type": DROP_METADATA (int),
    "drop_id": string,
    "version": string (optional),
    "nonce": string (optional)
    }
    :param conn: socket.accept() connection
    :return: None
    """
    file_location = get_drop_location(request['drop_id'])
    drop_version = DropVersion(int(request['version']), int(request['nonce']))
    drop_metadata = DropMetadata.read_file(
        request['drop_id'], drop_version, file_location,
    )

    response = {
        'status': 'ok',
        'response': drop_metadata.encode(),
    }

    send_response(conn, response)


def handle_request_file_metadata(request: dict, conn: socket.socket) -> None:
    """
    :param request:
    {
    "protocol_version": int,
    "request_type": FILE_METADATA (int),
    "file_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    pass


def handle_request_chunk_list(request: dict, conn: socket.socket) -> None:
    """
    :param request:
    {
    "protocol_version": int,
    "request_type": CHUNK_LIST (int),
    "file_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    pass


def handle_request_chunk(request: dict, conn: socket.socket) -> None:
    """
    :param request:
    {
    "protocol_version": int,
    "request_type": CHUNK (int),
    "file_id": string,
    "index": string,
    }
    :param conn: socket.accept() connection
    :return: None
    """
    pass


def handle_request_new_drop_metadata(request: dict, conn: socket.socket) \
        -> None:
    """
    :param request:
    {
    "protocol_version": int,
    "request_type": NEW_DROP_METADATA (int),
    "latest_version_id": int,
    "latest_version_nonce": int
    }
    :param conn: socket.accept() connection
    :return: None
    """
    pass


def main() -> None:
    """

    :return:
    """
    tcp_ip = sys.argv[1]
    tcp_port = sys.argv[2]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, int(tcp_port)))
    s.listen(5)

    while 1:
        conn, addr = s.accept()
        print(type(conn))
        print('Connection address:', addr)
        request = None
        while 1:
            data = conn.recv(DEFAULT_BUFFER_SIZE)
            if not data:
                break
            if request is None:
                request = data
            else:
                request += data
            print('Data received')
        s.shutdown(SHUT_RD)
        request_dispatcher(bencode.decode(request), conn)
        s.close()


if __name__ == '__main__':
    main()
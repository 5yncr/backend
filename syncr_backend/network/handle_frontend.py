import asyncio
import os
import platform
import socket
from typing import Any
from typing import Awaitable  # noqa
from typing import Callable  # noqa
from typing import Dict

import bencode  # type: ignore

from syncr_backend.constants import ACTION_ACCEPT_CHANGES
from syncr_backend.constants import ACTION_ACCEPT_CONFLICT_FILE
from syncr_backend.constants import ACTION_ADD_FILE
from syncr_backend.constants import ACTION_ADD_OWNER
from syncr_backend.constants import ACTION_DECLINE_CHANGES
from syncr_backend.constants import ACTION_DECLINE_CONFLICT_FILE
from syncr_backend.constants import ACTION_DELETE_DROP
from syncr_backend.constants import ACTION_GET_CONFLICTING_FILES
from syncr_backend.constants import ACTION_GET_OWNED_DROPS
from syncr_backend.constants import ACTION_GET_SELECT_DROPS
from syncr_backend.constants import ACTION_GET_SUB_DROPS
from syncr_backend.constants import ACTION_INITIALIZE_DROP
from syncr_backend.constants import ACTION_INPUT_DROP_TO_SUBSCRIBE_TO
from syncr_backend.constants import ACTION_REMOVE_FILE
from syncr_backend.constants import ACTION_REMOVE_OWNER
from syncr_backend.constants import ACTION_REQUEST_CHANGE
from syncr_backend.constants import ACTION_SHARE_DROP
from syncr_backend.constants import ACTION_TRANSFER_OWNERSHIP
from syncr_backend.constants import ACTION_UNSUBSCRIBE
from syncr_backend.constants import ACTION_VIEW_CONFLICTS
from syncr_backend.constants import ACTION_VIEW_PENDING_CHANGES
from syncr_backend.constants import ERR_INVINPUT
from syncr_backend.constants import FRONTEND_TCP_ADDRESS
from syncr_backend.constants import FRONTEND_UNIX_ADDRESS
from syncr_backend.init.drop_init import initialize_drop
from syncr_backend.metadata.drop_metadata import DropMetadata
from syncr_backend.util.drop_util import get_drop_metadata
from syncr_backend.util.drop_util import get_drop_peers
from syncr_backend.util.drop_util import get_owned_drops_metadata
from syncr_backend.util.drop_util import get_subscribed_drops_metadata
from syncr_backend.util.drop_util import simple_get_drop_metadata
from syncr_backend.util.drop_util import sync_drop
from syncr_backend.util.drop_util import update_drop
from syncr_backend.util.network_util import sync_send_response as send_response


def handle_frontend_request(
        request: Dict[str, Any], conn: socket.socket,
) -> None:

    function_map = {
        ACTION_ACCEPT_CHANGES: handle_accept_changes,
        ACTION_ACCEPT_CONFLICT_FILE: handle_accept_conflict_file,
        ACTION_ADD_FILE: handle_add_file,
        ACTION_ADD_OWNER: handle_add_owner,
        ACTION_DECLINE_CHANGES: handle_decline_changes,
        ACTION_DECLINE_CONFLICT_FILE: handle_decline_conflict_file,
        ACTION_DELETE_DROP: handle_delete_drop,
        ACTION_GET_CONFLICTING_FILES: handle_get_conflicting_files,
        ACTION_GET_OWNED_DROPS: handle_get_owned_drops,
        ACTION_GET_SELECT_DROPS: handle_get_selected_drops,
        ACTION_GET_SUB_DROPS: handle_get_subscribed_drops,
        ACTION_INPUT_DROP_TO_SUBSCRIBE_TO: handle_input_subscribe_drop,
        ACTION_INITIALIZE_DROP: handle_initialize_drop,
        ACTION_REMOVE_FILE: handle_remove_file,
        ACTION_REMOVE_OWNER: handle_remove_owner,
        ACTION_REQUEST_CHANGE: handle_request_change,
        ACTION_SHARE_DROP: handle_share_drop,
        ACTION_TRANSFER_OWNERSHIP: handle_transfer_ownership,
        ACTION_UNSUBSCRIBE: handle_unsubscribe,
        ACTION_VIEW_CONFLICTS: handle_view_conflicts,
        ACTION_VIEW_PENDING_CHANGES: handle_view_pending_changes,
    }  # type: Dict[str, Callable[[Dict[str, Any], socket.socket], Awaitable[None]]]  # noqa

    action = request['action']
    handle_function = function_map.get(action)

    if handle_function is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
        send_response(conn, response)
    else:
        asyncio.get_event_loop().run_until_complete(
            handle_function(request, conn),
        )


async def handle_accept_changes(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to accept changes in a file.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to apply changes to current file.
        # TODO: Test if given drop_ids and file_paths are valid.
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'changes accepted',
        }

    send_response(conn, response)


async def handle_transfer_ownership(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to transfer ownership from one drop to
    another.
    :param request:
    {
    'action': string
    'transfer_owner_id' : string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    if request['transfer_owner_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to apply ownership transfer.
        new_owner = request['transfer_owner_id']
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'Primary Ownership transferred to ' + new_owner,
        }

    send_response(conn, response)


async def handle_accept_conflict_file(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to accept a file that is in conflict with another.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to accept a conflict file and decline others.
        # TODO: Test if given drop_id and file_path are valid.
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'file accepted',
        }

    send_response(conn, response)


async def handle_add_file(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to add a file to a drop.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'file added to drop',
        }

        update_drop(
            request['drop_id'],
            add_file=request['file_path'],
        )

        peers = await get_drop_peers(request['drop_id'])
        meta = await get_drop_metadata(request['drop_id'], peers)

        if os.path.basename(request['file_path']) not in meta.files:
            response = {
                'status': 'error',
                'result': 'failure',
                'message': 'file was not added to the drop',

            }

    send_response(conn, response)


async def handle_add_owner(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to an owner to a drop
    :param request:
    {
    "action": string
    "drop_id": string
    "owner_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['owner_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'owner successfully added',
        }

        update_drop(
            request['drop_id'],
            add_secondary_owner=request['owner_id'],
        )

        md = await simple_get_drop_metadata(request['drop_id'])

        if request['owner_id'] not in md.other_owners:
            response['result'] = 'failure'
            response['message'] = 'unable to add owner to drop'

    send_response(conn, response)


async def handle_decline_changes(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to decline changes in a file.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to decline a change - leaving drop unchanged
        # TODO: Test if given drop_id and file_path are valid.
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'changes declined',
        }

    send_response(conn, response)


async def handle_decline_conflict_file(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to decline a file that is in conflict with another.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to decline a file in conflict with others
        # TODO: Test if given drop_id and file_path are valid.
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'conflicting file declined',
        }

    send_response(conn, response)


async def handle_delete_drop(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to delete a drop.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to delete a drop
        # TODO: Test if given drop_id is valid.
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'drop successfully deleted',
        }

    send_response(conn, response)


async def handle_get_conflicting_files(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to view files in drop that conflict each other.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: backend logic to retrieve list of conflicting files.
        # TODO: Test if given drop_id and file_path are valid.
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'conflicting files retrieved',
        }

    send_response(conn, response)


async def handle_get_owned_drops(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to retrieve drops owned by individual.
    :param request:
    {
    "action": string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    owned_drops = await get_owned_drops_metadata()
    drop_dictionaries = []
    for drop in owned_drops:
        drop_dictionaries.append(drop_metadata_to_response(drop))

    response = {
        'status': 'ok',
        'result': 'success',
        'requested_drops': drop_dictionaries,
        'message': 'owned drops retrieved',
    }

    send_response(conn, response)


async def handle_get_selected_drops(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to a drop selected by user.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        md = await simple_get_drop_metadata(request['drop_id'])
        drop = drop_metadata_to_response(md)

        response = {
            'status': 'ok',
            'result': 'success',
            'requested_drops': drop,
            'message': 'selected files retrieved',
        }

        if drop is None:
            response = {
                'status': 'error',
                'result': 'failure',
                'requested_drops': {},
                'message': 'drop retrieval failed',
            }

    send_response(conn, response)


async def handle_get_subscribed_drops(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to retrieve drops that user is subscribed to.
    :param request:
    {
    "action": string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    subscribed_drops = await get_subscribed_drops_metadata()
    drop_dictionaries = []
    for drop in subscribed_drops:
        drop_dictionaries.append(drop_metadata_to_response(drop))

    response = {
        'status': 'ok',
        'result': 'success',
        'requested_drops': drop_dictionaries,
        'message': 'subscribed drops retrieved',
    }

    send_response(conn, response)


async def handle_input_subscribe_drop(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to subscribe to drop that user specifies.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_path": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_path'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:

        try:
            await sync_drop(request['drop_id'], request['file_path'])
            response = {
                'status': 'ok',
                'result': 'success',
                'message': 'subscribed to drop ' + request['drop_id'],
            }
        except RuntimeError:
            response = {
                'status': 'error',
                'result': 'failure',
                'message': 'Cannot subscribe to drop!',
            }

    send_response(conn, response)


async def handle_initialize_drop(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to create drop whose name is specified by user.
    :param request:
    {
    "action": string
    "drop_name": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    # This code assumes that the user has already
    # created a folder to initialize as a drop.
    #
    # First, we check to see if tracker already contains drop id
    # If so, do nothing, send message failure back
    #
    # Else, initialize directory with 'drop_name' as the name of the drop

    # TODO: Allow user to select directory location from UI (on frontend).

    directory = request['directory']
    drop_name = os.path.basename(directory)

    status = 'error'
    result = 'failure'

    # TODO: Change 'False' to check if drop id already exists in tracker
    if False:
        message = 'A drop already exists with the given drop name'
    else:

        try:
            await initialize_drop(directory)
        except RuntimeError:
            message = 'Error in initializing drop.'
        else:
            status = 'ok'
            result = 'success'
            message = 'Drop ' + drop_name + 'created'

    response = {
        'status': status,
        'result': result,
        'message': message,
    }

    send_response(conn, response)


async def handle_remove_file(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to remove file from drop.
    :param request:
    {
    "action": string
    "drop_id": string
    "file_name": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None or request['file_name'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'file removed from drop',
        }

        update_drop(
            request['drop_id'],
            remove_file=os.path.basename(request['file_path']),
        )

        peers = await get_drop_peers(request['drop_id'])
        meta = await get_drop_metadata(request['drop_id'], peers)

        if os.path.basename(request['file_path']) in meta.files:
            response = {
                'status': 'error',
                'result': 'failure',
                'message': 'file was not removed from the drop',

            }

    send_response(conn, response)


async def handle_remove_owner(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to remove an owner from a drop
    :param request:
    {
    "action": string
    "drop_id": string
    "owner_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    if request['drop_id'] is None or request['owner_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'owner successfully removed',
        }

        await update_drop(
            request['drop_id'],
            remove_secondary_owner=request['owner_id'],
        )

        md = await simple_get_drop_metadata(request['drop_id'])

        if request['owner_id'] in md.other_owners:
            response['result'] = 'failure'
            response['message'] = 'unable to remove owner from drop'

    send_response(conn, response)


async def handle_request_change(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to request a change in the drop.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """

    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: Add given changes to list of requested changes.
        # TODO: Handle if given drop_id is not valid
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'pending changes submitted',
        }

    send_response(conn, response)


async def handle_share_drop(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to retrieve id that can be shared with other nodes.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: Backend logic to get drop info to share to others.
        # TODO: Handle if given drop_id is not valid
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'drop information retrieved',
        }

    send_response(conn, response)


async def handle_unsubscribe(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to unsubscribe from a subscribed drop.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: Backend logic to unsubscribe from drop.
        # TODO: Handle if given drop_id is not valid
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'unsubscribed from drop ' + request['drop_id'],
        }

    send_response(conn, response)


async def handle_view_conflicts(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to view conflicting files in drop.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: Backend logic to retrieve conflicting files in drop.
        # TODO: Handle if given drop_id is not valid
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'conflicting files retrieved',
        }

    send_response(conn, response)


async def handle_view_pending_changes(
        request: Dict[str, Any], conn: socket.socket,
) -> None:
    """
    Handling function to view pending changes in the drop.
    :param request:
    {
    "action": string
    "drop_id": string
    }
    :param conn: socket.accept() connection
    :return: None
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        # TODO: Backend logic to retrieve pending changes of drop.
        # TODO: Handle if given drop_id is not valid
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'pending changes retrieved',
        }

    send_response(conn, response)


# Helper functions for structure of responses
def drop_metadata_to_response(md: DropMetadata) -> Dict[str, Any]:
    """
    Converts dropMetadata object into frontend readable dictionary.
    :param md: DropMetadata object
    :return: Dictionary for frontend
    """
    response = {
        'drop_id': md.id,
        'name': md.name,
        'version': md.version,
        'previous_versions': md.previous_versions,
        'primary_owner': md.owner,
        'other_owners': md.other_owners,
        'signed_by': md.signed_by,
        'files': md.files,
        'sig': md.sig,
    }

    return response


# Functions for handling incoming frontend requests
def handle_request() -> None:
    """
    Listens for request from frontend and then sends response
    :return:
    """

    op_sys = platform.system()
    if op_sys == 'Windows':
        _tcp_handle_request()
    else:
        _unix_handle_request()


def _tcp_handle_request() -> None:
    """
    Listens for request from frontend and sends response over tcp socket
    :return:
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(FRONTEND_TCP_ADDRESS)
    s.listen(1)

    while True:
        conn, addr = s.accept()

        # Read request from frontend
        request = b''
        while True:
            data = conn.recv(4096)
            if not data:
                break
            else:
                request += data

        handle_frontend_request(bencode.decode(request), conn)


def _unix_handle_request() -> None:
    """
    Listens for request from frontend and sends response over unix socket
    :return:
    """

    try:
        os.unlink(FRONTEND_UNIX_ADDRESS)
    except OSError:
        # does not yet exist, do nothing
        pass

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(FRONTEND_UNIX_ADDRESS)

    s.listen(1)

    while True:
        conn, addr = s.accept()

        # Read request from frontend
        request = b''
        while True:
            data = conn.recv(4096)
            if not data:
                break
            else:
                request += data

        handle_frontend_request(bencode.decode(request), conn)


if __name__ == '__main__':
    handle_request()

"""Frontend handler.

Includes functions for setting up the frontend listner
and handling all the different requests.
"""
import asyncio
import os
import platform
import sys
import traceback
from typing import Any
from typing import Awaitable  # noqa
from typing import Callable  # noqa
from typing import Dict
from typing import List  # noqa

import bencode  # type: ignore

from syncr_backend.constants import DEFAULT_DROP_METADATA_LOCATION
from syncr_backend.constants import ERR_EXCEPTION
from syncr_backend.constants import ERR_INVINPUT
from syncr_backend.constants import ERR_NEXIST
from syncr_backend.constants import FRONTEND_TCP_ADDRESS
from syncr_backend.constants import FRONTEND_UNIX_ADDRESS
from syncr_backend.constants import FrontendAction
from syncr_backend.external_interface.drop_peer_store import send_drops_once
from syncr_backend.init.drop_init import initialize_drop
from syncr_backend.init.node_init import get_full_init_directory
from syncr_backend.init.node_init import load_private_key_from_disk
from syncr_backend.metadata.drop_metadata import DropMetadata
from syncr_backend.metadata.drop_metadata import get_drop_location
from syncr_backend.network.send_requests import get_my_ip
from syncr_backend.util import crypto_util
from syncr_backend.util.crypto_util import node_id_from_private_key
from syncr_backend.util.drop_util import check_for_changes
from syncr_backend.util.drop_util import check_for_update
from syncr_backend.util.drop_util import cleanup_drop
from syncr_backend.util.drop_util import do_metadata_request
from syncr_backend.util.drop_util import find_changes_in_new_version
from syncr_backend.util.drop_util import get_drop_metadata
from syncr_backend.util.drop_util import get_file_names_percent
from syncr_backend.util.drop_util import get_owned_subscribed_drops_metadata
from syncr_backend.util.drop_util import make_new_version
from syncr_backend.util.drop_util import queue_sync
from syncr_backend.util.log_util import get_logger
from syncr_backend.util.network_util import send_response


logger = get_logger(__name__)


async def handle_frontend_request(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Handle a request from the frontend.

    :param request: The request dict
    :param conn: The StreamWriter to write the response to
    """
    function_map = {
        FrontendAction.ADD_OWNER: handle_add_owner,
        FrontendAction.DELETE_DROP: handle_delete_drop,
        FrontendAction.GET_OWNED_SUBSCRIBED_DROPS:
            handle_get_owned_subscribed_drops,
        FrontendAction.GET_SELECTED_DROP: handle_get_selected_drop,
        FrontendAction.INPUT_DROP_TO_SUBSCRIBE_TO: handle_input_subscribe_drop,
        FrontendAction.INITIALIZE_DROP: handle_initialize_drop,
        FrontendAction.REMOVE_OWNER: handle_remove_owner,
        FrontendAction.SHARE_DROP: handle_share_drop,
        FrontendAction.UNSUBSCRIBE: handle_unsubscribe,
        FrontendAction.NEW_VERSION: handle_make_new_version,
        FrontendAction.PENDING_CHANGES: handle_pending_changes,
        FrontendAction.SYNC_UPDATE: handle_sync_update,
        FrontendAction.GET_PUBLIC_KEY: handle_get_public_key,
    }  # type: Dict[str, Callable[[Dict[str, Any], asyncio.StreamWriter], Awaitable[None]]]  # noqa

    action = request['action']
    handle_function = function_map.get(action)

    if handle_function is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
        await send_response(conn, response)
    else:
        try:
            await handle_function(request, conn)
        except Exception as e:
            response = {
                'status': 'error',
                'error': ERR_EXCEPTION,
                'message': str(e),
            }
            ex_type, ex, tb = sys.exc_info()
            logger.error("Error handling request: %s", e)
            traceback.print_exc()
            await send_response(conn, response)


async def handle_add_owner(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Handle adding an owner to a drop.

    :param request: {"action": string, "drop_id": string, "owner_id": string}
    :param conn: the streamwriter to respond with
    """
    if request.get('drop_id') is None or request.get('owner_id') is None:
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
        drop_id = crypto_util.b64decode(request['drop_id'])
        owner_id = crypto_util.b64decode(request['owner_id'])

        await make_new_version(
            drop_id,
            add_secondary_owner=owner_id,
        )

        md = await get_drop_metadata(drop_id, [])

        if owner_id not in md.other_owners:
            response['result'] = 'failure'
            response['message'] = 'unable to add owner to drop'

    await send_response(conn, response)


async def handle_make_new_version(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """Handle a make new version request.

    Tries to make a new version and returns the result.

    :param request: {"action": string, "drop_id": string}
    :param conn: The streamwriter
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        drop_id = crypto_util.b64decode(request['drop_id'])

        await make_new_version(drop_id)

        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'new version created',
        }

    await send_response(conn, response)


async def handle_delete_drop(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Delete a drop.

    :param request: {"action": string, "drop_id": string}
    :param conn: the streamwriter
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        drop_id = crypto_util.b64decode(request['drop_id'])
        file_location = await get_drop_location(drop_id)
        file_location = os.path.join(
            file_location,
            DEFAULT_DROP_METADATA_LOCATION,
        )
        drop_metadata = await DropMetadata.read_file(
            id=drop_id,
            metadata_location=file_location,
            version=None,
        )
        if drop_metadata is None:
            response = {
                'status': 'error',
                'error': ERR_INVINPUT,
            }
        else:
            await drop_metadata.delete()
            response = {
                'status': 'ok',
                'result': 'success',
                'message': 'drop successfully deleted',
            }

    await send_response(conn, response)


async def handle_sync_update(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Update a drop to a newer versions.

    :param request: {"action": string, "drop_id": string}
    :param conn: asyncio StreamWriter connection
    """
    drop_id = request.get('drop_id')
    logger.info("trying to update %s", request.get('drop_id'))
    if drop_id is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        drop_id = crypto_util.b64decode(drop_id)
        file_location = await get_drop_location(drop_id)
        drop_metadata_location = os.path.join(
            file_location,
            DEFAULT_DROP_METADATA_LOCATION,
        )
        drop_metadata = await DropMetadata.read_file(
            id=drop_id,
            metadata_location=drop_metadata_location,
            get_latest=False,
            version=None,
        )

        new_metadata = await DropMetadata.read_file(
            id=drop_id,
            metadata_location=drop_metadata_location,
            get_latest=True,
            version=None,
        )
        if new_metadata is None or drop_metadata is None:
            response = {
                'status': 'error',
                'error': ERR_NEXIST,
            }
        elif new_metadata.version > drop_metadata.version:
            logger.info("current: %s", drop_metadata.version)
            logger.info("latest: %s", new_metadata.version)
            logger.info("queuing sync")
            await queue_sync(
                drop_id, file_location, new_metadata.version,
            )
            await cleanup_drop(
                drop_id, drop_metadata, new_metadata,
            )
            response = {
                'status': 'ok',
                'result': 'success',
                'message': 'drop successfully updated',
            }
        else:
            response = {
                'status': 'error',
                'error': 'New version was not found',
            }

    await send_response(conn, response)


async def handle_get_selected_drop(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Get selected drop.

    Just calls _handle_selected_drop with get_pending_changes set to false.

    :param request: The request dict (see _handle_selected_drop)
    :param conn: The streamwriter
    """
    await _handle_selected_drop(False, request, conn)


async def handle_pending_changes(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Get pending changes.

    Just calls _handle_selected_drop with get_pending_changes set to true.

    :param request: the request dict (see _handle_selected_drop)
    :param conn: the streamwriter
    """
    await _handle_selected_drop(True, request, conn)


async def _handle_selected_drop(
    get_pending_changes: bool, request: Dict[str, Any],
    conn: asyncio.StreamWriter,
) -> None:
    """
    Get information about a drop.

    Note: get_pending_changes controls whether to check for pending changes.

    :param get_pending_changes: whether to check to filesystem and network
        for local or remote changes
    :param request: {"action": string, "drop_id": string}
    :param conn: the streamwriter
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        drop_id = crypto_util.b64decode(request['drop_id'])
        md = await get_drop_metadata(drop_id, [])
        drop = await drop_metadata_to_response(md)
        remote_pending_changes = {}  # type: Dict[str, List[str]]
        if get_pending_changes:
            file_update_status = await check_for_changes(drop_id)
            if file_update_status is None:
                local_pending_changes = {}  # type: Dict[str, List[str]]
            else:
                local_pending_changes = {
                    'added': list(file_update_status.added),
                    'removed': list(file_update_status.removed),
                    'changed': list(file_update_status.changed),
                    'unchanged': list(file_update_status.unchanged),
                }

            new_metadata, new_version_available = \
                await check_for_update(drop_id)
            if new_version_available and new_metadata is not None:
                remote_update_status = await find_changes_in_new_version(
                    drop_id, new_metadata,
                )
                if remote_update_status is not None:
                    remote_pending_changes = {
                        'added': list(remote_update_status.added),
                        'removed': list(remote_update_status.removed),
                        'changed': list(remote_update_status.changed),
                        'unchanged': list(remote_update_status.unchanged),
                    }
        else:
            local_pending_changes = {}
        if drop is None:
            response = {
                'status': 'error',
                'result': 'failure',
                'requested_drops': {},
                'message': 'drop retrieval failed',
            }
        else:
            response = {
                'status': 'ok',
                'result': 'success',
                'message': 'selected files retrieved',
                'requested_drops': {
                    'drop': drop,
                    'pending_changes': local_pending_changes,
                    'remote_pending_changes': remote_pending_changes,
                },
            }

    print(response)
    await send_response(conn, response)


async def handle_get_owned_subscribed_drops(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Retrieve drops that user owns and is subscribed to.

    :param request: {"action": string}
    :param conn: the streamwriter
    """
    md_tup = await get_owned_subscribed_drops_metadata()

    owned_drop_dictionaries = []
    subscribed_drop_dictionaries = []

    owned_drops = md_tup[0]
    subscribed_drops = md_tup[1]

    for drop in owned_drops:
        owned_drop_dictionaries.append(await drop_metadata_to_response(drop))

    for drop in subscribed_drops:
        subscribed_drop_dictionaries.append(
            await drop_metadata_to_response(drop),
        )

    dict_tup = (owned_drop_dictionaries, subscribed_drop_dictionaries)

    response = {
        'status': 'ok',
        'result': 'success',
        'requested_drops_tuple': dict_tup,
        'message': 'owned and subscribed drops retrieved.',
    }

    await send_response(conn, response)


async def handle_input_subscribe_drop(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Subscribe to drop that user specifies.

    :param request: {"action": string, "drop_id": string, "file_path": string}
    :param conn: the streamwriter
    """
    if request.get('drop_id') is None or request.get('directory') is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:

        drop_id = crypto_util.b64decode(request['drop_id'])
        file_path = request['directory']

        metadata = await do_metadata_request(drop_id, [])

        if metadata is None:
            response = {
                'status': 'error',
                'error': ERR_INVINPUT,
            }
            await send_response(conn, response)
            return

        name = metadata.name
        full_path = os.path.join(file_path, name)

        try:
            await queue_sync(drop_id, full_path)
            response = {
                'status': 'ok',
                'result': 'success',
                'message': 'subscribed to drop ' + name,
            }
        except RuntimeError:
            response = {
                'status': 'error',
                'result': 'failure',
                'message': 'Cannot subscribe to drop!',
            }

    await send_response(conn, response)


async def handle_initialize_drop(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Create drop whose name is specified by user.

    :param request: {"action": string, "drop_name": string}
    :param conn: the streamwriter
    """
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
            message = 'Drop ' + drop_name + ' created'
            await send_drops_once(*(get_my_ip()))

    response = {
        'status': status,
        'result': result,
        'message': message,
    }

    await send_response(conn, response)


async def handle_remove_owner(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Remove an owner from a drop.

    :param request: {"action": string, "drop_id": string, "owner_id": string}
    :param conn: the streamwriter
    """
    if request['drop_id'] is None or request['owner_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        drop_id = crypto_util.b64decode(request['drop_id'])
        owner_id = crypto_util.b64decode(request['owner_id'])
        response = {
            'status': 'ok',
            'result': 'success',
            'message': 'owner successfully removed',
        }

        await make_new_version(
            drop_id,
            remove_secondary_owner=owner_id,
        )

        md = await get_drop_metadata(drop_id, [])

        if owner_id in md.other_owners:
            response['result'] = 'failure'
            response['message'] = 'unable to remove owner from drop'

    await send_response(conn, response)


async def handle_share_drop(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Retrieve id that can be shared with other nodes.

    :param request: {"action": string, "drop_id": string}
    :param conn: the streamwriter
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

    await send_response(conn, response)


async def handle_unsubscribe(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Unsubscribe from a subscribed drop request.

    :param request: {"action": string, "drop_id": string}
    :param conn: the streamwriter
    """
    if request['drop_id'] is None:
        response = {
            'status': 'error',
            'error': ERR_INVINPUT,
        }
    else:
        drop_id = crypto_util.b64decode(request['drop_id'])
        file_location = await get_drop_location(drop_id)
        file_location = os.path.join(
            file_location, DEFAULT_DROP_METADATA_LOCATION,
        )
        drop_metadata = await DropMetadata.read_file(
            id=drop_id,
            metadata_location=file_location,
            version=None,
        )
        if drop_metadata is None:
            response = {
                'status': 'error',
                'error': ERR_INVINPUT,
            }
        else:
            drop_metadata.unsubscribe()
            response = {
                'status': 'ok',
                'result': 'success',
                'message': 'unsubscribed from drop ' + request['drop_id'],
            }

    await send_response(conn, response)


async def handle_get_public_key(
    request: Dict[str, Any], conn: asyncio.StreamWriter,
) -> None:
    """
    Handle request for public key (where public key is actually the node id).

    :param request: {"action": string}
    :param conn: the streamwriter
    """
    this_node_id = await node_id_from_private_key(
        await load_private_key_from_disk(),
    )
    if this_node_id is None:
        response = {
            'status': 'error',
            'error': 'Unable to retrieve node id',
        }
    else:
        public_key = crypto_util.b64encode(this_node_id)
        response = {
            'status': 'ok',
            'result': 'success',
            'message': public_key,
        }

    await send_response(conn, response)


# Helper functions for structure of responses
async def drop_metadata_to_response(md: DropMetadata) -> Dict[str, Any]:
    """
    Convert a DropMetadata object into frontend readable dictionary.

    :param md: DropMetadata object
    :return: Dictionary for frontend
    """
    files = await get_file_names_percent(md.id)
    response = {
        'drop_id': crypto_util.b64encode(md.id),
        'name': md.name,
        'version': "%s" % md.version,
        'previous_versions': ["%s" % v for v in md.previous_versions],
        'primary_owner': crypto_util.b64encode(md.owner),
        'other_owners': [crypto_util.b64encode(o) for o in md.other_owners],
        'signed_by': crypto_util.b64encode(md.signed_by),
        'files': {n: int(p*100) for n, p in files.items()},
    }

    return response


# Functions for handling incoming frontend requests
async def setup_frontend_server() -> asyncio.events.AbstractServer:
    """
    Listen for requests from frontend and then send responses.

    :return: An asyncio Server, either Unix socket or TCP socket
    """
    op_sys = platform.system()
    if op_sys == 'Windows':
        return await _tcp_handle_request()
    else:
        return await _unix_handle_request()


async def async_handle_request(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
) -> None:
    """
    Handle an async request.

    Reads from reader, then call function dispatcher.

    :param reader: The StreamReader to read from
    :param writer: The StreamWriter the response will go to
    """
    request = b''

    while 1:
        data = await reader.read()
        if not data:
            break
        else:
            request += data
    await handle_frontend_request(bencode.decode(request), writer)


async def _tcp_handle_request() -> asyncio.events.AbstractServer:
    """
    Listen for requests from frontend and send response over tcp socket.

    :return: An asyncio Server for TCP requests
    """
    return await asyncio.start_server(
        async_handle_request,
        host=FRONTEND_TCP_ADDRESS[0],
        port=FRONTEND_TCP_ADDRESS[1],
    )


async def _unix_handle_request() -> asyncio.events.AbstractServer:
    """
    Listen for requests from frontend and send response over unix socket.

    :return: An asyncio Server for Unix sockets
    """
    try:
        os.unlink(
            os.path.join(get_full_init_directory(), FRONTEND_UNIX_ADDRESS),
        )
    except OSError:
        # does not yet exist, do nothing
        pass

    return await asyncio.start_unix_server(
        async_handle_request, path=os.path.join(
            get_full_init_directory(), FRONTEND_UNIX_ADDRESS,
        ),
    )


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(setup_frontend_server())
    asyncio.get_event_loop().run_forever()

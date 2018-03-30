import socket

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
from syncr_backend.constants import ACTION_INPUT_DROP_TO_SUBSCRIBE_TO
from syncr_backend.constants import ACTION_INPUT_NAME
from syncr_backend.constants import ACTION_REMOVE_FILE
from syncr_backend.constants import ACTION_REMOVE_OWNER
from syncr_backend.constants import ACTION_REQUEST_CHANGE
from syncr_backend.constants import ACTION_SHARE_DROP
from syncr_backend.constants import ACTION_UNSUBSCRIBE
from syncr_backend.constants import ACTION_VIEW_CONFLICTS
from syncr_backend.constants import ACTION_VIEW_PENDING_CHANGES
from syncr_backend.util.network_util import send_response


def handle_frontend_request(request: dict, conn: socket.socket) -> None:

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
        ACTION_INPUT_NAME: handle_input_name,
        ACTION_REMOVE_FILE: handle_remove_file,
        ACTION_REMOVE_OWNER: handle_remove_owner,
        ACTION_REQUEST_CHANGE: handle_request_change,
        ACTION_SHARE_DROP: handle_share_drop,
        ACTION_UNSUBSCRIBE: handle_unsubscribe,
        ACTION_VIEW_CONFLICTS: handle_view_conflicts,
        ACTION_VIEW_PENDING_CHANGES: handle_view_pending_changes,
    }

    if request['action'] is None:
        response = {
            'status': 'error',
        }
        send_response(conn, response)
    else:
        action = function_map['action']
        if action is None:
            pass

    pass


def handle_accept_changes(request: dict, conn: socket.socket) -> None:
    pass


def handle_accept_conflict_file(request: dict, conn: socket.socket) -> None:
    pass


def handle_add_file(request: dict, conn: socket.socket) -> None:
    pass


def handle_add_owner(request: dict, conn: socket.socket) -> None:
    pass


def handle_decline_changes(request: dict, conn: socket.socket) -> None:
    pass


def handle_decline_conflict_file(request: dict, conn: socket.socket) -> None:
    pass


def handle_delete_drop(request: dict, conn: socket.socket) -> None:
    pass


def handle_get_conflicting_files(request: dict, conn: socket.socket) -> None:
    pass


def handle_get_owned_drops(request: dict, conn: socket.socket) -> None:
    pass


def handle_get_selected_drops(request: dict, conn: socket.socket) -> None:
    pass


def handle_get_subscribed_drops(request: dict, conn: socket.socket) -> None:
    pass


def handle_input_subscribe_drop(request: dict, conn: socket.socket) -> None:
    pass


def handle_input_name(request: dict, conn: socket.socket) -> None:
    pass


def handle_remove_file(request: dict, conn: socket.socket) -> None:
    pass


def handle_remove_owner(request: dict, conn: socket.socket) -> None:
    pass


def handle_request_change(request: dict, conn: socket.socket) -> None:
    pass


def handle_share_drop(request: dict, conn: socket.socket) -> None:
    pass


def handle_unsubscribe(request: dict, conn: socket.socket) -> None:
    pass


def handle_view_conflicts(request: dict, conn: socket.socket) -> None:
    pass


def handle_view_pending_changes(request: dict, conn: socket.socket) -> None:
    pass

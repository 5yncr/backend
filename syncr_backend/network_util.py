import socket
from socket import SHUT_WR


def send_response(conn: socket.socket, response: dict) -> None:
    """
    Sends a response to a connection and then closes writing to that connection
    :param conn: socket.accept() connection
    :param response: bencoded response
    :return: None
    """
    conn.send(response)
    conn.shutdown(SHUT_WR)

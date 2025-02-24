# https://docs.python.org/3/library/socket.html#example
import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8080
NUM_CONNS = 5


def contruct_response(response_payload: bytes = b"Request received!") -> bytes:
    response_line = b"HTTP/1.1 200 OK\r\n"
    headers = b"".join(
        [b"Server: CrappyServer/0.0.1\r\n", b"Content-Type: text/plain\r\n"]
    )
    blank_line = b"\r\n"

    response = b"".join([response_line, headers, blank_line, response_payload])

    return response


def start_server(
    response: bytes, host: str = HOST, port: int = PORT
) -> tuple[str, str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(NUM_CONNS)
    print("Server_listening at:", s.getsockname())

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)

        if not data:
            break

        print(f"\n[{datetime.now()}]")
        print("Server_new_connection_from:", addr)
        print("Server_request:\n", data.decode("utf-8"))
        print("\nServer_response:\n", response.decode("utf-8"))

        conn.sendall(response)
        conn.close()

    return response.decode("utf-8"), data.decode("utf-8")


def main():
    start_server(response=contruct_response())


if __name__ == "__main__":
    print("Starting standalone server...")
    main()

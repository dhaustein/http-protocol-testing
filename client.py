# https://docs.python.org/3/library/socket.html#example
import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 8080


def send_request(
    request_payload: bytes, host: str = HOST, port: int = PORT
) -> tuple[str, str]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        response_line = b"HTTP/1.1 200 OK\r\n"
        headers = b"".join(
            [b"User-Agent: CrappyClient/0.0.1\r\n", b"Content-Type: text/plain\r\n"]
        )
        blank_line = b"\r\n"

        request = b"".join([response_line, headers, blank_line, request_payload])
        s.sendall(request)
        data = s.recv(1024)

    print(f"\n[{datetime.now()}]")
    print("Client_request:\n", request.decode("utf-8"))
    print("\nClient_response:\n", data.decode("utf-8"))

    # return what was sent and received as if it was used in other parts of the application
    return request.decode("utf-8"), data.decode("utf-8")


def main():
    send_request(
        b"Default client request payload",
    )


if __name__ == "__main__":
    main()

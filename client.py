import argparse
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

    return request.decode("utf-8"), data.decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HTTP Client with configurable request"
    )
    parser.add_argument(
        "-r",
        "--request",
        dest="request",
        type=str,
        default="Default client request payload",
        help="Custom request payload in plaintest (default: 'Default client request payload')",
    )
    parser.add_argument(
        "-s",
        "--host",
        dest="host",
        type=str,
        default=HOST,
        help=f"Server host (default: {HOST})",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        default=PORT,
        help=f"Server port (default: {PORT})",
    )

    args = parser.parse_args()

    request_payload = args.request.encode("utf-8")
    send_request(request_payload, args.host, args.port)


if __name__ == "__main__":
    main()

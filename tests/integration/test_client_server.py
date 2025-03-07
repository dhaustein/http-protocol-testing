import random
import threading
import time
from typing import Callable, Generator, TypeAlias

import pytest

from client import send_request
from server import construct_response, start_server

# fun with types
ServerThread: TypeAlias = threading.Thread
ServerPort: TypeAlias = int
ServerFactoryCallable = Callable[[bytes], tuple[ServerThread, ServerPort]]
ServerFactoryFixture = Generator[ServerFactoryCallable, None, None]


# this is ugly, these asserts should probably run implicitly for almost every test case automatically
def assert_server_response_compliant(response: str) -> None:
    """Pretending these are actual HTTP compliancy checks"""
    assert "HTTP/1.1 200 OK" in response
    assert "Server: CrappyServer/0.0.1" in response
    assert "Content-Type: text/plain" in response


def assert_client_request_compliant(request: str) -> None:
    """Pretending these are actual HTTP compliancy checks"""
    assert "User-Agent: CrappyClient/0.0.1" in request
    assert "Content-Type: text/plain" in request


@pytest.fixture(scope="function")
def server_factory() -> ServerFactoryFixture:
    """Creates and manages test HTTP server instances with configurable responses
    Starts the server in a separate thread and stops it after the test completes

    Returns:
        A factory function that takes a response_payload parameter and returns
        a tuple containing:
            - thread: The server thread instance
            - port: The randomly assigned port number (8081-9000)

    Example:
        def test_custom_response(server_factory: ServerFactory) -> None:
            thread, port = server_factory(b"Custom Response")
            request, response = send_request(b"Test", port=port)
            assert "Custom Response" in response
    """
    threads = []

    def create_server(
        response_payload: bytes,
    ) -> tuple[threading.Thread, int]:
        # ugly hack to randomly assign the port to get around port collision
        port = random.randint(8081, 9080)

        def run_server() -> None:
            start_server(construct_response(response_payload), port=port)

        thread = threading.Thread(target=run_server, daemon=True)
        threads.append((thread, port))
        thread.start()
        time.sleep(0.1)  # should be replaced with a proper polling/readiness check

        return thread, port

    yield create_server

    for thread, _ in threads:
        thread.join(timeout=1)


def test_custom_server_responses(server_factory: ServerFactoryCallable) -> None:
    thread, port = server_factory(b"Custom Response")
    request, response = send_request(b"Test request", port=port)

    assert "Custom Response" in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


@pytest.mark.parametrize("response_payload", [b"Call 1", b"Call 2", b"Hello yet again"])
def test_multiple_subsequent_calls(
    server_factory: ServerFactoryCallable, response_payload: bytes
) -> None:
    thread, port = server_factory(response_payload)
    request, response = send_request(b"Test request", port=port)

    assert response_payload.decode() in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_empty_request_response(server_factory: ServerFactoryCallable) -> None:
    thread, port = server_factory(b"")
    request, response = send_request(b"", port=port)

    assert "HTTP/1.1 200 OK" in response
    assert "Content-Type: text/plain" in response
    assert "Request received!" not in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_extra_long_request_payload_rejected(
    server_factory: ServerFactoryCallable,
) -> None:
    """Test that a request larger than the default buffer size of 1024 the server
    will reject this with 'Connection reset by peer'"""
    thread, port = server_factory(b"Request received!")
    very_long_payload = b"bla" * 100000000

    with pytest.raises(ConnectionResetError):
        request, response = send_request(very_long_payload, port=port)


def test_special_characters_payload(server_factory: ServerFactoryCallable) -> None:
    special_chars = b"!@#$%^&*()\n\t"
    thread, port = server_factory(b"Request received!")

    request, response = send_request(special_chars, port=port)

    assert special_chars.decode() in request
    assert "Request received!" in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_unicode_payload(server_factory: ServerFactoryCallable) -> None:
    unicode_payload = "Grzegorz Brzęczyszczykiewicz かわいい猫".encode("utf-8")

    thread, port = server_factory(b"Request received!")

    request, response = send_request(unicode_payload, port=port)
    assert unicode_payload.decode() in request
    assert "Request received!" in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_max_num_connections(server_factory: ServerFactoryCallable) -> None:
    """Test server can handle up to 5 (by default) simultaneous connections"""
    thread, port = server_factory(b"Request received!")
    threads = []
    responses = {}

    def make_request(n: int) -> None:
        request, response = send_request(f"Connection {n}".encode(), port=port)
        responses[n] = response

    for i in range(5):
        t = threading.Thread(target=make_request, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for i in range(5):
        assert "Request received!" in responses[i]


def test_over_max_num_connections(server_factory: ServerFactoryCallable) -> None:
    """Test server will refuse more than default amount of 5 simultaneous connections"""
    pass


def test_request_timeout(server_factory: ServerFactoryCallable) -> None:
    """Test client handles server timeout"""
    pass


def test_content_encoding(server_factory: ServerFactoryCallable) -> None:
    """Test server properly handles and responds with gzip/deflate content"""
    pass


def test_redirect_handling(server_factory: ServerFactoryCallable) -> None:
    """Test server sends proper 3xx redirects and client can follow them"""
    pass


def test_chunked_transfer_encoding(server_factory: ServerFactoryCallable) -> None:
    """Test server can chunk large responses in chunks and client can properly
    reconstruct them"""
    pass


def test_connection_keep_alive(server_factory: ServerFactoryCallable) -> None:
    """Test server honors Connection: keep-alive header"""
    pass


def test_malformed_http_headers(server_factory: ServerFactoryCallable) -> None:
    """Test server properly handles malformed headers"""
    pass


def test_other_http_methods(server_factory: ServerFactoryCallable) -> None:
    """Test server correctly implements HEAD, GET, POST etc"""
    pass


def test_content_negotiation(server_factory: ServerFactoryCallable) -> None:
    """Test server respects Accept headers and returns content in correct format"""
    pass


def test_rate_limiting(server_factory: ServerFactoryCallable) -> None:
    """Test server/client can deal with 429 Too Many Requests"""
    pass


def test_partial_content(server_factory: ServerFactoryCallable) -> None:
    """Test server/client handles 206 Partial Content"""
    pass

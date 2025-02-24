import random
import threading
import time
from typing import Generator

import pytest

from client import send_request
from server import contruct_response, start_server


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
def server_factory() -> Generator:
    """Creates and manages test HTTP server instances with configurable responses
    Starts the server in a separate thread and stops it after the test completes

    Returns:
        A factory function that takes a response_payload parameter and returns
        a tuple containing:
            - thread: The server thread instance
            - port: The randomly assigned port number (8081-9000)

    Example:
        def test_custom_response(server_factory):
            thread, port = server_factory(b"Custom Response")
            request, response = send_request(b"Test", port=port)
            assert "Custom Response" in response
    """
    threads = []

    def create_server(
        response_payload: bytes = b"Request received!",
    ) -> tuple[threading.Thread, int]:
        # ugly hack to randomly assign the port to get around port collision
        port = random.randint(8081, 9080)

        def run_server():
            start_server(contruct_response(response_payload), port=port)

        thread = threading.Thread(target=run_server, daemon=True)
        threads.append((thread, port))
        thread.start()
        time.sleep(0.1)

        return thread, port

    yield create_server

    for thread, _ in threads:
        thread.join(timeout=1)


def test_custom_server_responses(server_factory):
    thread, port = server_factory(b"Custom Response")
    request, response = send_request(b"Test request", port=port)

    assert "Custom Response" in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


@pytest.mark.parametrize("response_payload", [b"Call 1", b"Call 2", b"Hello yet again"])
def test_multiple_subsequent_calls(server_factory, response_payload):
    thread, port = server_factory(response_payload)
    request, response = send_request(b"Test request", port=port)

    assert response_payload.decode() in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_empty_request_response(server_factory):
    thread, port = server_factory(b"")
    request, response = send_request(b"", port=port)

    assert "HTTP/1.1 200 OK" in response
    assert "Content-Type: text/plain" in response
    assert "Request received!" not in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_extra_long_request_payload_rejected(server_factory):
    """Test that a request larger than the default buffer size of 1024 the server
    will reject this with 'Connection reset by peer'
    """
    thread, port = server_factory()
    very_long_payload = b"bla" * 1000000000

    with pytest.raises(ConnectionResetError):
        request, response = send_request(very_long_payload, port=port)


def test_special_characters_payload(server_factory):
    special_chars = b"!@#$%^&*()\n\t"
    thread, port = server_factory()

    request, response = send_request(special_chars, port=port)

    assert special_chars.decode() in request
    assert "Request received!" in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


def test_unicode_payload(server_factory):
    unicode_payload = "Grzegorz Brzęczyszczykiewicz かわいい猫".encode("utf-8")

    thread, port = server_factory()

    request, response = send_request(unicode_payload, port=port)
    assert unicode_payload.decode() in request
    assert "Request received!" in response
    assert_client_request_compliant(request)
    assert_server_response_compliant(response)


# TODO make this actually parallel
def test_max_num_connections(server_factory):
    """Test server can handle up to 5 simultaneous connections"""
    thread, port = server_factory()
    # Test exactly NUM_CONNS (5)
    for i in range(5):
        request, response = send_request(f"Connection {i}".encode(), port=port)
        assert "Request received!" in response


# TODO make this actually parallel
def test_over_max_num_connections(server_factory):
    """Test server refuses more than 5 simultaneous connections"""
    thread, port = server_factory()
    # Test more than the allowed NUM_CONNS (5)
    for i in range(7):
        request, response = send_request(f"Connection {i}".encode(), port=port)
        assert "Request received!" in response

from unittest.mock import Mock, patch

import pytest  # noqa: F401

from client import send_request


def test_send_request() -> None:
    """Test client with a mocked server response

    We pretend-check the client is 'HTTP complicant' by checking it includes the expected headers
    """
    payload = b"test payload"
    request = b"GET / HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nUser-Agent: CrappyClient/0.0.1\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\ntest payload"
    response = b"HTTP/1.1 200 OK\r\nServer: CrappyServer/0.0.1\r\nContent-Type: text/plain\r\n\r\nRequest received!"

    # mock the server response
    mock_socket = Mock()
    mock_socket.recv.return_value = response

    with patch("socket.socket") as mock_socket_creator:
        # need to mock the context manager
        mock_socket_creator.return_value.__enter__.return_value = mock_socket

        actual_response = send_request(payload)

        mock_socket.connect.assert_called_once_with(("127.0.0.1", 8080))
        mock_socket.sendall.assert_called_once_with(request)

        expected = (request.decode("utf-8"), response.decode("utf-8"))

        # there would be more to assert to make sure the client is sending HTTP protocol compliant requests
        assert actual_response == expected

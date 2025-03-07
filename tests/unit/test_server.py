from unittest.mock import Mock, patch

import pytest  # noqa: F401

from server import construct_response, start_server


def test_server_connection() -> None:
    """Test server with a mocked client connection

    We mock the socker and fake a client request and check the server response is 'HTTP compliant'
    """
    host = "127.0.0.1"
    port = 8888
    client_request = b"HTTP/1.1 200 OK\r\nUser-Agent: CrappyClient/0.0.1\r\nContent-Type: text/plain\r\n\r\ntest payload from client"
    server_response = construct_response(b"My test response")

    mock_conn = Mock()
    mock_socket = Mock()
    mock_conn.recv.return_value = client_request
    mock_socket.accept.return_value = (mock_conn, (host, port))

    # break the while loop after the first connection
    mock_conn.recv.side_effect = [client_request, b""]

    with patch("socket.socket") as mock_socket_creator:
        mock_socket_creator.return_value = mock_socket

        # throw away the echoed server data, they would be empty anyway
        actual_response, _ = start_server(server_response, port=port, host=host)

        mock_socket.setsockopt.assert_called_once()
        mock_socket.bind.assert_called_once_with((host, port))
        mock_socket.listen.assert_called_once_with(5)
        mock_conn.sendall.assert_called_once_with(server_response)
        mock_conn.close.assert_called_once()

        assert actual_response == server_response.decode("utf-8")
        assert "Server: CrappyServer/0.0.1" in actual_response
        assert "Content-Type: text/plain" in actual_response

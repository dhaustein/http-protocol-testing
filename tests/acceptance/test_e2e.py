import time
from typing import Generator

import podman  # type: ignore
import pytest

# utility functions


def get_container_logs(container_id: str) -> str:  # type: ignore
    """Retrieves container logs/stdout"""
    pass


# environment setup as fixtures


@pytest.fixture
def podman_network() -> Generator[str, None, None]:
    """Creates a podman network"""
    # note that this is not necessary when NOT running the containers on a single host
    client = podman.PodmanClient()
    network = client.networks.create("test-network")
    yield network.name
    network.remove()


@pytest.fixture
def server_container(podman_network: str) -> Generator[str, None, None]:
    """Starts server container"""
    client = podman.PodmanClient()
    container = client.containers.run(
        "http-server:latest",
        command="python server.py --response-payload 'Test Response'",
        network=podman_network,
        name="test-server",
        detach=True,
    )
    time.sleep(10)  # wait for server to start
    yield "test-server"
    container.stop()
    container.remove()


@pytest.fixture
def client_container(podman_network: str) -> Generator[str, None, None]:
    """Starts client container"""
    client = podman.PodmanClient()
    container = client.containers.run(
        "http-client:latest", network=podman_network, name="test-client", detach=True
    )
    yield container.id
    container.stop()
    container.remove()


# example test cases


def test_basic_http_communication(server_container: str, client_container: str) -> None:
    """Test basic HTTP request-response cycle"""
    client = podman.PodmanClient()
    container = client.containers.get(client_container)

    exit_code, output = container.exec_run(
        f"python client.py --host {server_container} --request 'Test Request'"
    )

    assert exit_code == 0
    assert "Test Response" in output.decode()
    assert "HTTP/1.1 200 OK" in output.decode()


def test_http_headers_compliance(server_container: str, client_container: str) -> None:
    """Test HTTP headers format compliance"""
    pass

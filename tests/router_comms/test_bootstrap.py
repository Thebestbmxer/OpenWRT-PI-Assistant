"""Tests for router bootstrap."""

from unittest.mock import MagicMock, patch

import paramiko
import pytest

from openwrt_controller.router_comms.discovery.bootstrap import (
    DEFAULT_PASSWORDS,
    DEFAULT_USERNAME,
    BootstrapCredentials,
    RouterBootstrap,
) 
from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from openwrt_controller.router_comms.exceptions import (
    AuthenticationError,
    InitialCommunicationError,
)

@pytest.fixture
def candidate():
    """Return a test router candidate."""

    return RouterCandidate(
        address="192.168.50.1",
        ssh_port=22,
    )


def test_default_bootstrap_username(candidate):
    bootstrap = RouterBootstrap(candidate)

    assert bootstrap.username == DEFAULT_USERNAME
    assert bootstrap.username == "root"


def test_default_bootstrap_passwords(candidate):
    bootstrap = RouterBootstrap(candidate)

    assert bootstrap.passwords == DEFAULT_PASSWORDS
    assert bootstrap.passwords == ("", "password")


def test_bootstrap_tries_blank_password_first(candidate):
    client = MagicMock()
    transport = MagicMock()

    transport.is_authenticated.return_value = True

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ), patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.Transport",
        return_value=transport,
    ):
        bootstrap = RouterBootstrap(candidate)

        connected_client, credentials = bootstrap.connect()

    assert connected_client is client
    assert isinstance(credentials, BootstrapCredentials)
    assert credentials.username == "root"
    assert credentials.password == ""

    transport.start_client.assert_called_once_with(timeout=5.0)
    transport.auth_none.assert_called_once_with("root")


def test_bootstrap_falls_back_to_password(candidate):
    blank_transport = MagicMock()
    blank_transport.auth_none.side_effect = paramiko.AuthenticationException()

    password_client = MagicMock()
    password_client.connect.return_value = None

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        side_effect=[MagicMock(), password_client],
    ), patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.Transport",
        return_value=blank_transport,
    ):
        bootstrap = RouterBootstrap(candidate)

        connected_client, credentials = bootstrap.connect()

    assert connected_client is password_client
    assert credentials.username == "root"
    assert credentials.password == "password"

    password_client.connect.assert_called_once_with(
        hostname="192.168.50.1",
        port=22,
        username="root",
        password="password",
        timeout=5.0,
        allow_agent=False,
        look_for_keys=False,
    )


def test_bootstrap_raises_authentication_error(candidate):
    transport = MagicMock()
    transport.auth_none.side_effect = paramiko.AuthenticationException()

    client = MagicMock()
    client.connect.side_effect = paramiko.AuthenticationException()

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ), patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.Transport",
        return_value=transport,
    ):
        bootstrap = RouterBootstrap(candidate)

        with pytest.raises(AuthenticationError):
            bootstrap.connect()


def test_bootstrap_raises_connection_error(candidate):
    transport = MagicMock()
    transport.start_client.side_effect = OSError("connection refused")

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=MagicMock(),
    ), patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.Transport",
        return_value=transport,
    ):
        bootstrap = RouterBootstrap(candidate)

        with pytest.raises(InitialCommunicationError):
            bootstrap.connect()


def test_bootstrap_disables_ssh_agent_and_existing_keys(candidate):
    client = MagicMock()
    client.connect.return_value = None

    bootstrap = RouterBootstrap(
        candidate,
        passwords=("password",),
    )

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ):
        bootstrap.connect()

    client.connect.assert_called_once_with(
        hostname="192.168.50.1",
        port=22,
        username="root",
        password="password",
        timeout=5.0,
        allow_agent=False,
        look_for_keys=False,
    )
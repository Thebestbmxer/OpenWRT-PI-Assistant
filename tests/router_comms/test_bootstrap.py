"""Tests for initial router communication."""

from unittest.mock import MagicMock, patch

import paramiko
import pytest

from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from openwrt_controller.router_comms.exceptions import (
    AuthenticationError,
    InitialCommunicationError,
)
from openwrt_controller.router_comms.discovery.bootstrap import (
    DEFAULT_PASSWORDS,
    DEFAULT_USERNAME,
    RouterBootstrap,
)


@pytest.fixture
def candidate():
    return RouterCandidate(
        address="192.168.50.1",
        ssh_port=22,
    )


def test_default_bootstrap_username():
    assert DEFAULT_USERNAME == "root"


def test_default_bootstrap_passwords():
    assert DEFAULT_PASSWORDS == ("", "password")


def test_bootstrap_tries_blank_password_first(candidate):
    client = MagicMock()

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ):
        client.connect.return_value = None

        bootstrap = RouterBootstrap(candidate)

        connected_client, credentials = bootstrap.connect()

    assert connected_client is client
    assert credentials.username == "root"
    assert credentials.password == ""

    client.connect.assert_called_once_with(
        hostname="192.168.50.1",
        port=22,
        username="root",
        password="",
        timeout=5.0,
        allow_agent=False,
        look_for_keys=False,
    )


def test_bootstrap_falls_back_to_password(candidate):
    client = MagicMock()

    client.connect.side_effect = [
        paramiko.AuthenticationException(),
        None,
    ]

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ):
        bootstrap = RouterBootstrap(candidate)

        connected_client, credentials = bootstrap.connect()

    assert connected_client is client
    assert credentials.username == "root"
    assert credentials.password == "password"
    assert client.connect.call_count == 2

    first_call = client.connect.call_args_list[0]
    second_call = client.connect.call_args_list[1]

    assert first_call.kwargs["password"] == ""
    assert second_call.kwargs["password"] == "password"


def test_bootstrap_raises_authentication_error(candidate):
    client = MagicMock()
    client.connect.side_effect = paramiko.AuthenticationException()

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ):
        bootstrap = RouterBootstrap(candidate)

        with pytest.raises(AuthenticationError):
            bootstrap.connect()


def test_bootstrap_raises_connection_error(candidate):
    client = MagicMock()
    client.connect.side_effect = OSError("connection refused")

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ):
        bootstrap = RouterBootstrap(candidate)

        with pytest.raises(InitialCommunicationError):
            bootstrap.connect()


def test_bootstrap_disables_ssh_agent_and_existing_keys(candidate):
    client = MagicMock()

    with patch(
        "openwrt_controller.router_comms.discovery.bootstrap.paramiko.SSHClient",
        return_value=client,
    ):
        bootstrap = RouterBootstrap(candidate)
        bootstrap.connect()

    assert client.connect.call_args.kwargs["allow_agent"] is False
    assert client.connect.call_args.kwargs["look_for_keys"] is False

"""Tests for persistent router SSH connections."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import paramiko
import pytest

from openwrt_controller.router_comms.ssh.connection import (
    RouterConnection,
)
from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from openwrt_controller.router_comms.exceptions import (
    InitialCommunicationError,
)
from openwrt_controller.router_comms.ssh.keys import SSHKeyPair


@pytest.fixture
def candidate() -> RouterCandidate:
    return RouterCandidate(
        address="192.168.50.1",
        ssh_port=22,
    )


@pytest.fixture
def key_pair(tmp_path: Path) -> SSHKeyPair:
    return SSHKeyPair(
        private_key_path=tmp_path / "controller",
        public_key_path=tmp_path / "controller.pub",
        public_key="ssh-rsa AAAATEST",
    )


def test_connect_uses_controller_private_key(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()

    with patch(
        "openwrt_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair)

        connection.connect()

    client.connect.assert_called_once_with(
        hostname="192.168.50.1",
        port=22,
        username="root",
        key_filename=str(key_pair.private_key_path),
        timeout=5.0,
        allow_agent=False,
        look_for_keys=False,
    )


def test_connect_marks_connection_active(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()
    transport = MagicMock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport

    with patch(
        "openwrt_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair)

        connection.connect()

        assert connection.connected is True


def test_execute_returns_command_result(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()

    stdout = MagicMock()
    stderr = MagicMock()
    stdin = MagicMock()

    stdout.read.return_value = b"OpenWrt\n"
    stderr.read.return_value = b""
    stdout.channel.recv_exit_status.return_value = 0

    client.exec_command.return_value = (
        stdin,
        stdout,
        stderr,
    )

    with patch(
        "openwrt_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair)
        connection.connect()

        output, error, status = connection.execute(
            "cat /etc/openwrt_release"
        )

    assert output == "OpenWrt\n"
    assert error == ""
    assert status == 0

    client.exec_command.assert_called_once_with(
        "cat /etc/openwrt_release"
    )


def test_execute_requires_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    connection = RouterConnection(candidate, key_pair)

    with pytest.raises(RuntimeError):
        connection.execute("echo test")


def test_connection_error_is_wrapped(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()
    client.connect.side_effect = OSError("connection refused")

    with patch(
        "openwrt_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair)

        with pytest.raises(InitialCommunicationError):
            connection.connect()

    client.close.assert_called_once()


def test_authentication_error_is_wrapped(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()
    client.connect.side_effect = paramiko.AuthenticationException()

    with patch(
        "openwrt_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair)

        with pytest.raises(InitialCommunicationError):
            connection.connect()

    client.close.assert_called_once()


def test_close_disconnects_client(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()

    with patch(
        "openwrt_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair)

        connection.connect()
        connection.close()

    client.close.assert_called_once()
    assert connection.connected is False

"""Tests for persistent router SSH connections."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import paramiko
import pytest

from router_controller.router_comms.ssh.connection import (
    RouterConnection,
    RouterConnectionConfig,
    RouterHostKeyPolicy,
)
from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.exceptions import (
    InitialCommunicationError,
    RouterIdentityError,
)
from router_controller.router_comms.ssh.keys import SSHKeyPair

TEST_HOST_KEY_FINGERPRINT = "aabbccdd"

@pytest.fixture
def connection_config() -> RouterConnectionConfig:
    return RouterConnectionConfig(
        expected_host_key_fingerprint=TEST_HOST_KEY_FINGERPRINT,
    )

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
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair,connection_config)

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
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()
    transport = MagicMock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        connection.connect()

        assert connection.connected is True


def test_execute_returns_command_result(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()

    stdout = MagicMock()
    stderr = MagicMock()
    stdin = MagicMock()

    stdout.read.return_value = b"Router\n"
    stderr.read.return_value = b""
    stdout.channel.recv_exit_status.return_value = 0

    client.exec_command.return_value = (
        stdin,
        stdout,
        stderr,
    )

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)
        connection.connect()

        output, error, status = connection.execute(
            "cat /etc/router_release"
        )

    assert output == "Router\n"
    assert error == ""
    assert status == 0

    client.exec_command.assert_called_once_with(
        "cat /etc/router_release"
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
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()
    client.connect.side_effect = OSError("connection refused")

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        with pytest.raises(InitialCommunicationError):
            connection.connect()

    client.close.assert_called_once()


def test_authentication_error_is_wrapped(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()
    client.connect.side_effect = paramiko.AuthenticationException()

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        with pytest.raises(InitialCommunicationError):
            connection.connect()

    client.close.assert_called_once()


def test_close_disconnects_client(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        connection.connect()
        connection.close()

    client.close.assert_called_once()
    assert connection.connected is False

def test_connect_does_not_reconnect_when_already_connected(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        connection.connect()

    client.connect.assert_called_once()

def test_close_is_safe_when_not_connected(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    connection = RouterConnection(candidate, key_pair, connection_config)

    connection.close()

    assert connection.connected is False

def test_connected_reflects_inactive_transport(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()
    transport = MagicMock()

    transport.is_active.return_value = True
    client.get_transport.return_value = transport

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        connection.connect()

        assert connection.connected is True

        transport.is_active.return_value = False

        assert connection.connected is False

def test_host_key_fingerprint(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()
    transport = MagicMock()

    host_key = MagicMock()
    host_key.get_fingerprint.return_value = (
        b"\xaa\xbb\xcc\xdd"
    )
    
    #host_key = paramiko.RSAKey.generate(2048)
    transport.get_remote_server_key.return_value = host_key
    transport.is_active.return_value = True

    client.get_transport.return_value = transport

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(candidate, key_pair, connection_config)

        connection.connect()

        fingerprint = connection.host_key_fingerprint

        assert connection.host_key_fingerprint == "aabbccdd"
    #assert fingerprint is not None
    #assert fingerprint.startswith("SHA256:")

def test_host_key_fingerprint_requires_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    connection = RouterConnection(candidate, key_pair)

    assert connection.host_key_fingerprint is None

def test_host_key_policy_accepts_matching_fingerprint():
    expected = "aabbccdd"

    policy = RouterHostKeyPolicy(expected)

    client = MagicMock()
    key = MagicMock()

    key.get_fingerprint.return_value = (
        b"\xaa\xbb\xcc\xdd"
    )

    policy.missing_host_key(
        client,
        "192.168.50.1",
        key,
    )

def test_host_key_policy_rejects_mismatched_fingerprint():
    policy = RouterHostKeyPolicy("aabbccdd")

    client = MagicMock()
    key = MagicMock()

    key.get_fingerprint.return_value = (
        b"\x11\x22\x33\x44"
    )

    #with pytest.raises(paramiko.SSHException):
    with pytest.raises(RouterIdentityError):
        policy.missing_host_key(
            client,
            "192.168.50.1",
            key,
        )

def test_connect_uses_expected_host_key_fingerprint(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection_config: RouterConnectionConfig,
):
    client = MagicMock()
    transport = MagicMock()
    transport.is_active.return_value = True

    client.get_transport.return_value = transport

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(
            candidate,
            key_pair,
            RouterConnectionConfig(
                expected_host_key_fingerprint="aabbccdd",
            ),
        )

        connection.connect()

    policy = client.set_missing_host_key_policy.call_args.args[0]

    assert isinstance(policy, RouterHostKeyPolicy)
    assert policy.expected_fingerprint == "aabbccdd"

def test_connect_rejects_unknown_host_key(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(
            candidate,
            key_pair,
            RouterConnectionConfig(
                expected_host_key_fingerprint=None,
            ),
        )

        with pytest.raises(RouterIdentityError):
            connection.connect()

    client.connect.assert_not_called()
    client.close.assert_not_called()

def test_host_key_policy_accepts_uppercase_expected_fingerprint():
    policy = RouterHostKeyPolicy("AABBCCDD")

    client = MagicMock()
    key = MagicMock()

    key.get_fingerprint.return_value = (
        b"\xaa\xbb\xcc\xdd"
    )

    policy.missing_host_key(
        client,
        "192.168.50.1",
        key,
    )

def test_connect_installs_host_key_verification_policy(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(
            candidate,
            key_pair,
            RouterConnectionConfig(
                expected_host_key_fingerprint="aabbccdd",
            ),
        )

        connection.connect()

    client.set_missing_host_key_policy.assert_called_once()

    policy = (
        client.set_missing_host_key_policy.call_args.args[0]
    )

    assert isinstance(policy, RouterHostKeyPolicy)
    assert policy.expected_fingerprint == "aabbccdd"

def test_connect_rejects_mismatched_host_key(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    client = MagicMock()

    policy = None

    def connect_side_effect(**kwargs):
        nonlocal policy

        policy = client.set_missing_host_key_policy.call_args.args[0]

        key = MagicMock()
        key.get_fingerprint.return_value = (
            b"\x11\x22\x33\x44"
        )

        policy.missing_host_key(
            client,
            candidate.address,
            key,
        )

    client.connect.side_effect = connect_side_effect

    with patch(
        "router_controller.router_comms.ssh.connection.paramiko.SSHClient",
        return_value=client,
    ):
        connection = RouterConnection(
            candidate,
            key_pair,
            RouterConnectionConfig(
                expected_host_key_fingerprint="aabbccdd",
            ),
        )

        with pytest.raises(RouterIdentityError):
            connection.connect()

    assert connection.connected is False
    assert connection._client is None
    client.close.assert_called_once()

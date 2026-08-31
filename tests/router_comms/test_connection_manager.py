"""Tests for router SSH connection management."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.ssh.connection_manager import (
    RouterConnectionManager,
)
from router_controller.router_comms.ssh.keys import SSHKeyPair


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


@pytest.fixture
def connection() -> MagicMock:
    connection = MagicMock()
    connection.connected = False
    return connection


def test_connect_creates_and_connects_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection: MagicMock,
):
    factory = MagicMock(return_value=connection)

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        connection_factory=factory,
    )

    result = manager.connect()

    factory.assert_called_once_with(candidate, key_pair)
    connection.connect.assert_called_once()

    assert result is connection
    assert manager.connection is connection


def test_connect_reuses_active_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection: MagicMock,
):
    connection.connected = True

    factory = MagicMock(return_value=connection)

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        connection_factory=factory,
    )

    first = manager.connect()
    second = manager.connect()

    assert first is connection
    assert second is connection

    factory.assert_called_once_with(candidate, key_pair)
    connection.connect.assert_not_called()


def test_connect_replaces_inactive_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection: MagicMock,
):
    connection.connected = False

    replacement = MagicMock()
    replacement.connected = True

    factory = MagicMock(side_effect=[connection, replacement])

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        connection_factory=factory,
    )

    manager.connect()
    result = manager.connect()

    connection.close.assert_called_once()
    replacement.connect.assert_called_once()

    assert result is replacement
    assert manager.connection is replacement


def test_disconnect_closes_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection: MagicMock,
):
    connection.connected = True

    factory = MagicMock(return_value=connection)

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        connection_factory=factory,
    )

    manager.connect()
    manager.disconnect()

    connection.close.assert_called_once()

    assert manager.connection is None
    assert manager.connected is False


def test_disconnect_is_safe_without_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    manager = RouterConnectionManager(
        candidate,
        key_pair,
    )

    manager.disconnect()

    assert manager.connection is None
    assert manager.connected is False


def test_reconnect_replaces_connection(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
):
    first = MagicMock()
    first.connected = True

    second = MagicMock()
    second.connected = True

    factory = MagicMock(side_effect=[first, second])

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        connection_factory=factory,
    )

    result1 = manager.connect()
    result2 = manager.reconnect()

    assert result1 is first
    assert result2 is second

    first.close.assert_called_once()
    second.connect.assert_called_once()

    assert manager.connection is second
    assert manager.connected is True


def test_connected_reflects_connection_state(
    candidate: RouterCandidate,
    key_pair: SSHKeyPair,
    connection: MagicMock,
):
    factory = MagicMock(return_value=connection)

    manager = RouterConnectionManager(
        candidate,
        key_pair,
        connection_factory=factory,
    )

    assert manager.connected is False

    connection.connected = True
    manager.connect()

    assert manager.connected is True

    connection.connected = False

    assert manager.connected is False

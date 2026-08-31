"""Tests for installing the controller SSH key on a router."""

from pathlib import Path
from unittest.mock import MagicMock

import paramiko
import pytest

from router_controller.router_comms.ssh.key_installer import (
    RouterKeyInstaller,
)
from router_controller.router_comms.ssh.keys import SSHKeyPair


@pytest.fixture
def key_pair(tmp_path: Path) -> SSHKeyPair:
    private_key = tmp_path / "controller"
    public_key = tmp_path / "controller.pub"

    private_key.write_text("PRIVATE KEY", encoding="utf-8")
    public_key.write_text(
        "ssh-rsa AAAATEST controller\n",
        encoding="utf-8",
    )

    return SSHKeyPair(
        private_key_path=private_key,
        public_key_path=public_key,
        public_key="ssh-rsa AAAATEST controller",
    )


@pytest.fixture
def client() -> MagicMock:
    client = MagicMock(spec=paramiko.SSHClient)

    transport = MagicMock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport

    stdin = MagicMock()
    stdout = MagicMock()
    stderr = MagicMock()

    stdout.channel.recv_exit_status.return_value = 0
    stderr.read.return_value = b""

    client.exec_command.return_value = (
        stdin,
        stdout,
        stderr,
    )

    return client


def test_installs_public_key(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)

    client.exec_command.assert_called_once()


def test_install_command_creates_ssh_directory_and_authorized_keys(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)

    command = client.exec_command.call_args.args[0]

    #assert "mkdir -p ~/.ssh" in command
    #assert "~/.ssh/authorized_keys" in command
    
    assert "mkdir -p /etc/dropbear" in command
    assert "/etc/dropbear/authorized_keys" in command


def test_install_command_contains_public_key(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)

    command = client.exec_command.call_args.args[0]

    assert key_pair.public_key in command


def test_install_is_idempotent(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)
    installer.install(key_pair)

    assert client.exec_command.call_count == 2


def test_install_preserves_existing_authorized_keys(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)

    command = client.exec_command.call_args.args[0]

    assert "authorized_keys" in command
    assert "grep" in command


def test_install_sets_ssh_directory_permissions(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)

    command = client.exec_command.call_args.args[0]

    #assert "chmod 700 ~/.ssh" in command
    assert "chmod 700 /etc/dropbear" in command


def test_install_sets_authorized_keys_permissions(
    client: MagicMock,
    key_pair: SSHKeyPair,
):
    installer = RouterKeyInstaller(client)

    installer.install(key_pair)

    command = client.exec_command.call_args.args[0]

    #assert "chmod 600 ~/.ssh/authorized_keys" in command
    assert "chmod 600 /etc/dropbear/authorized_keys" in command


def test_install_requires_authenticated_client(
    key_pair: SSHKeyPair,
):
    client = MagicMock(spec=paramiko.SSHClient)
    client.get_transport.return_value = None

    installer = RouterKeyInstaller(client)

    with pytest.raises(RuntimeError, match="SSH connection is not active"):
        installer.install(key_pair)


def test_install_wraps_ssh_errors(
    key_pair: SSHKeyPair,
):
    client = MagicMock(spec=paramiko.SSHClient)
    transport = MagicMock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport
    client.exec_command.side_effect = paramiko.SSHException(
        "remote command failed"
    )

    installer = RouterKeyInstaller(client)

    with pytest.raises(paramiko.SSHException):
        installer.install(key_pair)
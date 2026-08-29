from pathlib import Path
from unittest.mock import Mock

import pytest

from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from openwrt_controller.router_comms.provisioner import RouterProvisioner
from openwrt_controller.router_comms.ssh.keys import SSHKeyPair


@pytest.fixture
def candidate():
    return RouterCandidate(
        address="192.168.1.1",
        ssh_port=22,
    )


@pytest.fixture
def key_pair(tmp_path):
    return SSHKeyPair(
        private_key_path=tmp_path / "controller",
        public_key_path=tmp_path / "controller.pub",
        public_key="ssh-ed25519 AAAATEST controller",
    )


@pytest.fixture
def key_manager():
    return Mock()


@pytest.fixture
def discovery():
    return Mock()


@pytest.fixture
def bootstrap():
    return Mock()


@pytest.fixture
def connection():
    connection = Mock()
    connection.connected = True
    return connection


def create_provisioner(
    key_manager,
    discovery,
    bootstrap,
    connection,
):
    return RouterProvisioner(
        key_manager=key_manager,
        discovery=discovery,
        bootstrap_factory=Mock(return_value=bootstrap),
        connection_factory=Mock(return_value=connection),
    )


def test_provision_loads_existing_key(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    result = provisioner.provision(candidate)

    assert result == candidate

    key_manager.load_key_pair.assert_called_once_with()
    key_manager.generate_key_pair.assert_not_called()


def test_provision_generates_key_when_missing(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.side_effect = FileNotFoundError
    key_manager.generate_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    result = provisioner.provision(candidate)

    assert result == candidate

    key_manager.load_key_pair.assert_called_once_with()
    key_manager.generate_key_pair.assert_called_once_with()


def test_provision_discovers_when_candidate_not_supplied(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair
    discovery.discover.return_value = candidate

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    result = provisioner.provision()

    assert result == candidate
    discovery.discover.assert_called_once_with()


def test_provision_does_not_discover_when_candidate_supplied(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    provisioner.provision(candidate)

    discovery.discover.assert_not_called()


def test_provision_installs_public_key(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    provisioner.provision(candidate)

    assert client.close.called
    connection.connect.assert_called_once_with()


def test_bootstrap_connection_is_closed_when_install_fails(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
    monkeypatch,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    installer = Mock()
    installer.install.side_effect = RuntimeError("install failed")

    monkeypatch.setattr(
        "openwrt_controller.router_comms.provisioner.RouterKeyInstaller",
        Mock(return_value=installer),
    )

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    with pytest.raises(RuntimeError, match="install failed"):
        provisioner.provision(candidate)

    client.close.assert_called_once_with()
    connection.connect.assert_not_called()


def test_provision_connects_using_controller_key(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    provisioner.provision(candidate)

    assert provisioner.connection_factory.call_args.args == (
        candidate,
        key_pair,
    )

    connection.connect.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_provision_closes_bootstrap_before_permanent_connection(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    events = []

    client.close.side_effect = lambda: events.append("bootstrap-close")
    connection.connect.side_effect = lambda: events.append(
        "permanent-connect"
    )

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    provisioner.provision(candidate)

    assert events == [
        "bootstrap-close",
        "permanent-connect",
    ]


def test_provision_failure_to_connect_is_propagated(
    key_manager,
    discovery,
    bootstrap,
    connection,
    candidate,
    key_pair,
):
    key_manager.load_key_pair.return_value = key_pair

    client = Mock()
    bootstrap.connect.return_value = (client, Mock())

    connection.connect.side_effect = RuntimeError(
        "permanent connection failed"
    )

    provisioner = create_provisioner(
        key_manager,
        discovery,
        bootstrap,
        connection,
    )

    with pytest.raises(
        RuntimeError,
        match="permanent connection failed",
    ):
        provisioner.provision(candidate)

    connection.close.assert_called_once_with()
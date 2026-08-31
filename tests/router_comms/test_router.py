"""Tests for the Router device representation."""

from pathlib import Path

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.router.identity import RouterIdentity
from router_controller.router_comms.router.router import Router
from router_controller.router_comms.router.state import RouterState
from router_controller.router_comms.ssh.keys import SSHKeyPair


def test_router_can_store_state():
    identity = RouterIdentity(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key_fingerprint="SHA256:test",
    )

    candidate = RouterCandidate(
        address="192.168.50.1",
        ssh_port=22,
    )

    state = RouterState(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key="SHA256:test",
        ip_address="192.168.50.1",
    )

    router = Router(
        identity=identity,
        candidate=candidate,
        state=state,
    )

    assert router.identity is identity
    assert router.state is state
    assert router.candidate is candidate


def test_router_can_create_connection_manager(tmp_path: Path):
    identity = RouterIdentity(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key_fingerprint="SHA256:test",
    )

    candidate = RouterCandidate(
        address="192.168.50.1",
        ssh_port=22,
    )

    router = Router(
        identity=identity,
        candidate=candidate,
    )

    key_pair = SSHKeyPair(
        private_key_path=tmp_path / "controller",
        public_key_path=tmp_path / "controller.pub",
        public_key="ssh-rsa AAAATEST",
    )

    manager = router.create_connection_manager(key_pair)

    assert router.connection_manager is manager
    assert manager.candidate is candidate
    assert manager.key_pair is key_pair
    assert router.connected is False

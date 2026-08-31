from pathlib import Path

from router_controller.router_comms.router.state import RouterState
from router_controller.router_comms.router.repository import (
    RouterStateRepository,
)


def test_router_state_can_be_saved_and_loaded(tmp_path: Path):
    repository = RouterStateRepository(
        tmp_path / "router.json"
    )

    state = RouterState(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key="SHA256:test-key",
        ip_address="192.168.1.1",
    )

    repository.save(state)

    loaded = repository.load()

    assert loaded == state


def test_router_state_load_returns_none_when_missing(tmp_path: Path):
    repository = RouterStateRepository(
        tmp_path / "router.json"
    )

    assert repository.load() is None


def test_router_state_preserves_identity_when_ip_changes(tmp_path: Path):
    repository = RouterStateRepository(
        tmp_path / "router.json"
    )

    state = RouterState(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key="SHA256:test-key",
        ip_address="192.168.1.1",
    )

    repository.save(state)

    state.ip_address = "192.168.1.2"
    repository.save(state)

    loaded = repository.load()

    assert loaded is not None
    assert loaded.mac_address == "AA:BB:CC:DD:EE:FF"
    assert loaded.ssh_host_key == "SHA256:test-key"
    assert loaded.ip_address == "192.168.1.2"

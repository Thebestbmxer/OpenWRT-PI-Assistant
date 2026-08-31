from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.router import Router
from router_controller.router_comms.router_identity import RouterIdentity


def test_router_identity_stores_stable_identity():
    identity = RouterIdentity(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key_fingerprint="SHA256:test",
    )

    assert identity.mac_address == "AA:BB:CC:DD:EE:FF"
    assert identity.ssh_host_key_fingerprint == "SHA256:test"


def test_router_separates_identity_from_location():
    identity = RouterIdentity(
        mac_address="AA:BB:CC:DD:EE:FF",
        ssh_host_key_fingerprint="SHA256:test",
    )

    candidate = RouterCandidate(
        address="192.168.1.1",
        ssh_port=22,
        mac_address="AA:BB:CC:DD:EE:FF",
        interface="eth0",
    )

    router = Router(
        identity=identity,
        candidate=candidate,
    )

    assert router.identity.mac_address == "AA:BB:CC:DD:EE:FF"
    assert router.candidate.address == "192.168.1.1"
    assert router.candidate.interface == "eth0"

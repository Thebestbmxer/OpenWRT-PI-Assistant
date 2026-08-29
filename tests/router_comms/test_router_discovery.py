"""Tests for router discovery."""

from unittest.mock import patch

import pytest

from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
    RouterDiscovery,
)
from openwrt_controller.router_comms.exceptions import RouterNotFoundError


def test_discovery_returns_reachable_candidate():
    discovery = RouterDiscovery(
        networks=["192.168.50.0/24"],
    )

    with patch.object(
        discovery,
        "_port_is_open",
        return_value=True,
    ):
        candidate = discovery.discover()

    assert isinstance(candidate, RouterCandidate)
    assert candidate.address == "192.168.50.1"
    assert candidate.ssh_port == 22

def test_discovery_ignores_loopback_addresses():
    addresses = [
        "127.0.0.1",
        "127.0.1.1",
        "127.255.255.254",
        "192.168.50.1",
    ]

    discovered = [
        address
        for address in addresses
        if not router_discovery._is_local_address(address)
    ]

    assert "127.0.0.1" not in discovered
    assert "127.0.1.1" not in discovered
    assert "127.255.255.254" not in discovered
    assert "192.168.50.1" in discovered


def test_discovery_tries_addresses_in_network():
    discovery = RouterDiscovery(
        networks=["192.168.50.0/30"],
    )

    checked_addresses = []

    def fake_port_check(address, port):
        checked_addresses.append((address, port))
        return address == "192.168.50.2"

    with patch.object(
        discovery,
        "_port_is_open",
        side_effect=fake_port_check,
    ):
        candidate = discovery.discover()

    assert candidate.address == "192.168.50.2"
    assert ("192.168.50.1", 22) in checked_addresses
    assert ("192.168.50.2", 22) in checked_addresses


def test_discovery_raises_when_no_candidate_is_found():
    discovery = RouterDiscovery(
        networks=["192.168.50.0/30"],
    )

    with patch.object(
        discovery,
        "_port_is_open",
        return_value=False,
    ):
        with pytest.raises(RouterNotFoundError):
            discovery.discover()


def test_discovery_accepts_explicit_networks():
    discovery = RouterDiscovery(
        networks=["10.20.30.0/24"],
    )

    assert discovery._get_networks() == ["10.20.30.0/24"]


def test_discovery_does_not_authenticate():
    """Discovery only checks network reachability."""

    discovery = RouterDiscovery(
        networks=["192.168.50.0/30"],
    )

    with patch.object(
        discovery,
        "_port_is_open",
        return_value=True,
    ):
        candidate = discovery.discover()

    assert candidate.address == "192.168.50.1"

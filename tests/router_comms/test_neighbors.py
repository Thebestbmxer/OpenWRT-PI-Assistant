"""Tests for Linux neighbor discovery."""

from unittest.mock import MagicMock, patch

import pytest

from router_controller.router_comms.discovery.neighbors import (
    Neighbor,
    NeighborDiscovery,
)


def test_neighbor_parses_mac_and_interface():
    discovery = NeighborDiscovery()

    result = MagicMock()
    result.stdout = (
        "192.168.50.1 dev eth0 lladdr "
        "AA:BB:CC:DD:EE:FF REACHABLE\n"
    )

    with patch(
        "router_controller.router_comms.discovery.neighbors.subprocess.run",
        return_value=result,
    ) as run:
        neighbor = discovery.get_neighbor("192.168.50.1")

    run.assert_called_once_with(
        ["ip", "neigh", "show", "192.168.50.1"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert neighbor == Neighbor(
        address="192.168.50.1",
        mac_address="aa:bb:cc:dd:ee:ff",
        interface="eth0",
    )


def test_neighbor_handles_missing_entry():
    discovery = NeighborDiscovery()

    result = MagicMock()
    result.stdout = ""

    with patch(
        "router_controller.router_comms.discovery.neighbors.subprocess.run",
        return_value=result,
    ):
        neighbor = discovery.get_neighbor("192.168.50.1")

    assert neighbor == Neighbor(
        address="192.168.50.1",
    )


def test_neighbor_handles_entry_without_mac():
    discovery = NeighborDiscovery()

    result = MagicMock()
    result.stdout = (
        "192.168.50.1 dev eth0 INCOMPLETE\n"
    )

    with patch(
        "router_controller.router_comms.discovery.neighbors.subprocess.run",
        return_value=result,
    ):
        neighbor = discovery.get_neighbor("192.168.50.1")

    assert neighbor.address == "192.168.50.1"
    assert neighbor.interface == "eth0"
    assert neighbor.mac_address is None


def test_neighbor_handles_command_failure():
    discovery = NeighborDiscovery()

    with patch(
        "router_controller.router_comms.discovery.neighbors.subprocess.run",
        side_effect=OSError("ip command unavailable"),
    ):
        neighbor = discovery.get_neighbor("192.168.50.1")

    assert neighbor == Neighbor(
        address="192.168.50.1",
    )


def test_neighbor_handles_malformed_mac():
    discovery = NeighborDiscovery()

    result = MagicMock()
    result.stdout = (
        "192.168.50.1 dev eth0 lladdr not-a-mac REACHABLE\n"
    )

    with patch(
        "router_controller.router_comms.discovery.neighbors.subprocess.run",
        return_value=result,
    ):
        neighbor = discovery.get_neighbor("192.168.50.1")

    assert neighbor.address == "192.168.50.1"
    assert neighbor.interface == "eth0"
    assert neighbor.mac_address is None


def test_neighbor_rejects_invalid_ip():
    discovery = NeighborDiscovery()

    with pytest.raises(ValueError):
        discovery.get_neighbor("not-an-ip")


def test_neighbor_rejects_ipv6():
    discovery = NeighborDiscovery()

    with pytest.raises(ValueError):
        discovery.get_neighbor("fe80::1")


def test_neighbor_accepts_custom_ip_command():
    discovery = NeighborDiscovery(command="/usr/sbin/ip")

    result = MagicMock()
    result.stdout = (
        "192.168.50.1 dev eth0 lladdr "
        "aa:bb:cc:dd:ee:ff REACHABLE\n"
    )

    with patch(
        "router_controller.router_comms.discovery.neighbors.subprocess.run",
        return_value=result,
    ) as run:
        discovery.get_neighbor("192.168.50.1")

    run.assert_called_once_with(
        [
            "/usr/sbin/ip",
            "neigh",
            "show",
            "192.168.50.1",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

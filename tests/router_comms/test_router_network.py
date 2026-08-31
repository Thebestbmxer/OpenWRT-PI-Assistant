"""Tests for router network information."""

from unittest.mock import MagicMock


def test_get_mac_addresses():
    from router_controller.router_comms.router.network import (
        RouterNetworkInfo,
    )

    connection = MagicMock()

    connection.execute.return_value = (
        """1: lo: <LOOPBACK> mtu 65536
2: eth0: <BROADCAST,MULTICAST> mtu 1500 link/ether AA:BB:CC:DD:EE:FF
3: eth1: <BROADCAST,MULTICAST> mtu 1500 link/ether 11:22:33:44:55:66
4: br-lan: <BROADCAST,MULTICAST> mtu 1500 link/ether 22:33:44:55:66:77
""",
        "",
        0,
    )

    network = RouterNetworkInfo(connection)

    mac_addresses = network.get_mac_addresses()

    assert mac_addresses == {
        "eth0": "aa:bb:cc:dd:ee:ff",
        "eth1": "11:22:33:44:55:66",
        "br-lan": "22:33:44:55:66:77",
    }

    connection.execute.assert_called_once_with(
        "ip -o link show"
    )


def test_get_mac_addresses_ignores_interfaces_without_mac():
    from router_controller.router_comms.router.network import (
        RouterNetworkInfo,
    )

    connection = MagicMock()

    connection.execute.return_value = (
        """1: lo: <LOOPBACK> mtu 65536
2: eth0: <BROADCAST,MULTICAST> mtu 1500 link/ether AA:BB:CC:DD:EE:FF
""",
        "",
        0,
    )

    network = RouterNetworkInfo(connection)

    mac_addresses = network.get_mac_addresses()

    assert mac_addresses == {
        "eth0": "aa:bb:cc:dd:ee:ff",
    }


def test_get_mac_addresses_raises_when_command_fails():
    from router_controller.router_comms.router.network import (
        RouterNetworkInfo,
    )

    connection = MagicMock()

    connection.execute.return_value = (
        "",
        "command failed",
        1,
    )

    network = RouterNetworkInfo(connection)

    try:
        network.get_mac_addresses()
    except RuntimeError as exc:
        assert str(exc) == (
            "Unable to retrieve router network interfaces."
        )
    else:
        raise AssertionError(
            "Expected RuntimeError"
        )

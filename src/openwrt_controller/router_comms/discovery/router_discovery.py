"""Discovery of routers reachable from the controller."""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Iterable

from openwrt_controller.router_comms.exceptions import RouterNotFoundError


def _local_ipv4_addresses() -> set[str]:
    """Return IPv4 addresses assigned to this machine."""
    import subprocess

    addresses = {"127.0.0.1"}

    try:
        result = subprocess.run(
            ["ip", "-4", "-o", "addr", "show"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return addresses

    for line in result.stdout.splitlines():
        parts = line.split()

        try:
            address_with_prefix = parts[3]
            interface = ipaddress.ip_interface(address_with_prefix)

            if interface.version == 4:
                addresses.add(str(interface.ip))
        except (IndexError, ValueError):
            continue

    return addresses


def _is_local_address(address: str) -> bool:
    """Return True when an address belongs to this machine.

    Loopback addresses are always considered local. IPv4 addresses
    assigned to the controller are also considered local so discovery
    cannot select the controller itself as a router.
    """
    try:
        ip_address = ipaddress.ip_address(address)
    except ValueError:
        return False

    if ip_address.is_loopback:
        return True

    if ip_address.version == 4:
        return address in _local_ipv4_addresses()

    return False


@dataclass(frozen=True)
class RouterCandidate:
    """A router candidate discovered on a local network."""

    address: str
    ssh_port: int = 22


class RouterDiscovery:
    """Discover reachable router candidates.

    Discovery is intentionally limited to network discovery. It does
    not authenticate, execute commands, or modify the router.
    """

    def __init__(
        self,
        ssh_port: int = 22,
        timeout: float = 0.5,
        networks: Iterable[str] | None = None,
    ) -> None:
        self.ssh_port = ssh_port
        self.timeout = timeout
        self.networks = list(networks) if networks is not None else None

    def discover(self) -> RouterCandidate:
        """Return the first reachable router candidate."""

        for network in self._get_networks():
            for address in self._addresses_in_network(network):
                # Never attempt to connect to the controller itself.
                if _is_local_address(address):
                    continue

                if self._port_is_open(address, self.ssh_port):
                    return RouterCandidate(
                        address=address,
                        ssh_port=self.ssh_port,
                    )

        raise RouterNotFoundError(
            "No router candidate with an accessible SSH port was discovered."
        )

    def _get_networks(self) -> list[str]:
        """Return networks that should be searched.

        Explicitly supplied networks are used when provided. Otherwise,
        networks are derived from the controller's local IPv4 addresses.
        """
        if self.networks:
            return self.networks

        return self._get_local_networks()

    def _get_local_networks(self) -> list[str]:
        """Determine local IPv4 networks from active interfaces.

        Uses the Linux ``ip`` command rather than hostname resolution so
        discovery reflects the networks actually assigned to the controller.
        """
        import subprocess

        networks: list[str] = []

        try:
            result = subprocess.run(
                ["ip", "-4", "-o", "addr", "show", "scope", "global"],
                capture_output=True,
                text=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return networks

        for line in result.stdout.splitlines():
            parts = line.split()

            try:
                address_with_prefix = parts[3]
                interface = ipaddress.ip_interface(address_with_prefix)
            except (IndexError, ValueError):
                continue

            network = str(interface.network)

            if network not in networks:
                networks.append(network)

        return networks


    @staticmethod
    def _addresses_in_network(network: str) -> Iterable[str]:
        """Return usable host addresses within an IPv4 network."""
        parsed = ipaddress.ip_network(network, strict=False)

        return (str(address) for address in parsed.hosts())

    def _port_is_open(self, address: str, port: int) -> bool:
        """Return whether a TCP port is reachable."""
        try:
            with socket.create_connection(
                (address, port),
                timeout=self.timeout,
            ):
                return True
        except OSError:
            return False

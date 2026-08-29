"""Discovery of routers reachable from the controller."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import socket
from typing import Iterable

from openwrt_controller.router_comms.exceptions import (
    RouterNotFoundError,
)


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

        Explicitly supplied networks are used when provided. Automatic
        interface discovery is added separately so that it can be
        independently tested.
        """
        if self.networks:
            return self.networks

        return self._get_local_networks()

    def _get_local_networks(self) -> list[str]:
        """Determine local IPv4 networks.

        The initial implementation uses the hostname-resolved local
        addresses. This intentionally remains conservative until a
        platform-specific interface discovery implementation is added.
        """
        networks: list[str] = []

        hostname = socket.gethostname()

        try:
            addresses = socket.gethostbyname_ex(hostname)[2]
        except socket.gaierror:
            addresses = []

        for address in addresses:
            try:
                interface = ipaddress.ip_interface(f"{address}/24")
            except ValueError:
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

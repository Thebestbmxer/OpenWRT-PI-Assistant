"""Linux neighbor-table discovery."""

from __future__ import annotations

import ipaddress
import re
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Neighbor:
    """A network neighbor known to the controller."""

    address: str
    mac_address: str | None = None
    interface: str | None = None


class NeighborDiscovery:
    """Discover MAC addresses and interfaces using the Linux neighbor table."""

    def __init__(self, command: str = "ip") -> None:
        self.command = command

    def get_neighbor(self, address: str) -> Neighbor:
        """Return neighbor information for an IPv4 address.

        A missing or incomplete neighbor entry is not considered an error.
        """

        self._validate_address(address)

        try:
            result = subprocess.run(
                [self.command, "neigh", "show", address],
                capture_output=True,
                text=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return Neighbor(address=address)

        return self._parse_output(address, result.stdout)

    @staticmethod
    def _validate_address(address: str) -> None:
        """Validate that the supplied address is IPv4."""

        try:
            parsed = ipaddress.ip_address(address)
        except ValueError as exc:
            raise ValueError(
                f"Invalid IP address: {address}"
            ) from exc

        if parsed.version != 4:
            raise ValueError(
                f"Only IPv4 addresses are supported: {address}"
            )

    @staticmethod
    def _parse_output(address: str, output: str) -> Neighbor:
        """Parse output from ``ip neigh show``."""

        if not output.strip():
            return Neighbor(address=address)

        line = output.splitlines()[0]
        parts = line.split()

        interface: str | None = None
        mac_address: str | None = None

        try:
            dev_index = parts.index("dev")
            interface = parts[dev_index + 1]
        except (ValueError, IndexError):
            pass

        try:
            lladdr_index = parts.index("lladdr")
            candidate = parts[lladdr_index + 1]

            if _is_valid_mac(candidate):
                mac_address = candidate.lower()
        except (ValueError, IndexError):
            pass

        return Neighbor(
            address=address,
            mac_address=mac_address,
            interface=interface,
        )


_MAC_PATTERN = re.compile(
    r"^[0-9a-fA-F]{2}"
    r"(?::[0-9a-fA-F]{2}){5}$"
)


def _is_valid_mac(value: str) -> bool:
    """Return True when value is a valid colon-separated MAC address."""

    return bool(_MAC_PATTERN.fullmatch(value))

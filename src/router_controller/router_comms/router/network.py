"""Network information collected from a router."""

from __future__ import annotations

import re

from router_controller.router_comms.ssh.connection import RouterConnection


class RouterNetworkInfo:
    """Collect network information from a router."""

    def __init__(self, connection: RouterConnection) -> None:
        self.connection = connection

    def get_mac_addresses(self) -> dict[str, str]:
        """Return MAC addresses keyed by network interface."""

        stdout, _stderr, exit_status = self.connection.execute(
            "ip -o link show"
        )

        if exit_status != 0:
            raise RuntimeError(
                "Unable to retrieve router network interfaces."
            )

        mac_addresses: dict[str, str] = {}

        for line in stdout.splitlines():
            match = re.search(
                r"^\d+:\s+([^:]+):.*link/ether\s+([0-9a-fA-F:]{17})",
                line,
            )

            if match is None:
                continue

            interface = match.group(1)
            mac_address = match.group(2).lower()

            mac_addresses[interface] = mac_address

        return mac_addresses

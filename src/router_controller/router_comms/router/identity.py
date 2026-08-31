"""Router identity and identification data."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RouterIdentity:
    """Stable identity information for a router."""

    mac_address: str | None = None
    ssh_host_key_fingerprint: str | None = None

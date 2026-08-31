"""Persistent state for a known router."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass
class RouterState:
    """Persisted state describing a known router."""

    mac_address: str
    ssh_host_key: str
    ip_address: str
    ssh_port: int = 22
    username: str = "root"
    first_seen: str | None = None
    last_seen: str | None = None

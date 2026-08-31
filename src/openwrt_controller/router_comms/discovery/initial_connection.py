"""Discover a router and establish initial communication."""

from __future__ import annotations

from dataclasses import dataclass

import paramiko

from openwrt_controller.router_comms.discovery.bootstrap import (
    BootstrapCredentials,
    RouterBootstrap,
)
from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
    RouterDiscovery,
)
from openwrt_controller.router_comms.exceptions import (
    AuthenticationError,
    InitialCommunicationError,
    RouterNotFoundError,
)


@dataclass(frozen=True)
class RouterConnectionResult:
    """Result of router discovery and initial SSH communication."""

    candidate: RouterCandidate | None
    client: paramiko.SSHClient | None
    credentials: BootstrapCredentials | None
    connected: bool
    error: Exception | None = None


def discover_and_connect_router() -> RouterConnectionResult:
    """Discover a router and attempt initial SSH communication.

    Discovery determines which router address should be used.
    Bootstrap then attempts to establish an SSH connection using the
    currently configured bootstrap credentials.

    This function intentionally contains no UI logic so it can be called
    both when the welcome page loads and when the user selects
    "Search Again".
    """

    try:
        discovery = RouterDiscovery()
        candidate = discovery.discover()

    except RouterNotFoundError as exc:
        return RouterConnectionResult(
            candidate=None,
            client=None,
            credentials=None,
            connected=False,
            error=exc,
        )

    try:
        bootstrap = RouterBootstrap(
            candidate=candidate,
            passwords=("",),
        )

        client, credentials = bootstrap.connect()

        return RouterConnectionResult(
            candidate=candidate,
            client=client,
            credentials=credentials,
            connected=True,
        )

    except (
        AuthenticationError,
        InitialCommunicationError,
    ) as exc:
        return RouterConnectionResult(
            candidate=candidate,
            client=None,
            credentials=None,
            connected=False,
            error=exc,
        )

"""Management of a router's persistent SSH connection."""

from __future__ import annotations

from typing import Callable

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.ssh.connection import (
    RouterConnection,
    RouterConnectionConfig,
)
from router_controller.router_comms.ssh.keys import SSHKeyPair
from router_controller.router_comms.router.state import RouterState


class RouterConnectionManager:
    """Manage the lifecycle of a router SSH connection.

    The manager owns a RouterConnection instance and is responsible for
    establishing, reusing, disconnecting, and reconnecting that connection.

    It does not perform router discovery or persistence yet. Those concerns
    will be added at a higher level once the connection lifecycle is stable.
    """

    def __init__(
        self,
        candidate: RouterCandidate,
        key_pair: SSHKeyPair,
        state: RouterState | None = None,
        connection_factory: Callable[
            [RouterCandidate, SSHKeyPair, RouterConnectionConfig],
            RouterConnection,
        ] = RouterConnection,
    ) -> None:
        self.candidate = candidate
        self.key_pair = key_pair
        self.state = state
        self.connection_factory = connection_factory

        self._connection: RouterConnection | None = None

    def connect(self) -> RouterConnection:
        """Establish or reuse the router SSH connection."""

        if self._connection is not None:
            if self._connection.connected:
                return self._connection

            self._connection.close()
            self._connection = None

        connection = self.connection_factory(
            self.candidate,
            self.key_pair,
            self._connection_config(),
        )

        connection.connect()

        self._connection = connection

        return connection

    def disconnect(self) -> None:
        """Close the current router SSH connection."""

        if self._connection is None:
            return

        self._connection.close()
        self._connection = None

    def reconnect(self) -> RouterConnection:
        """Close the current connection and establish a new one."""

        self.disconnect()

        return self.connect()

    @property
    def connected(self) -> bool:
        """Return whether an active router connection exists."""

        return (
            self._connection is not None
            and self._connection.connected
        )

    @property
    def connection(self) -> RouterConnection | None:
        """Return the current connection, if one exists."""

        return self._connection

    def _connection_config(self) -> RouterConnectionConfig:
        """Build SSH configuration from persisted router state."""

        if self.state is None:
            return RouterConnectionConfig()

        return RouterConnectionConfig(
            username=self.state.username,
            expected_host_key_fingerprint=self.state.ssh_host_key,
        )

    def host_key_fingerprint(self) -> str | None:
        """Return the fingerprint of the connected router."""

        if self._connection is None:
            return None

        return self._connection.host_key_fingerprint

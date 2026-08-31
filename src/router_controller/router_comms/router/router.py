"""Router device representation."""

from dataclasses import dataclass, field

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.router.identity import RouterIdentity
from router_controller.router_comms.router.state import RouterState
from router_controller.router_comms.ssh.connection_manager import (
    RouterConnectionManager,
)
from router_controller.router_comms.ssh.keys import SSHKeyPair


@dataclass
class Router:
    """A known router managed by the controller."""

    identity: RouterIdentity
    candidate: RouterCandidate

    name: str | None = None
    model: str | None = None
    architecture: str | None = None
    target: str | None = None

    state: RouterState | None = None
    connection_manager: RouterConnectionManager | None = field(
        default=None,
        repr=False,
    )

    def create_connection_manager(
        self,
        key_pair: SSHKeyPair,
    ) -> RouterConnectionManager:
        """Create the SSH connection manager for this router."""

        manager = RouterConnectionManager(
            candidate=self.candidate,
            key_pair=key_pair,
        )

        self.connection_manager = manager

        return manager

    @property
    def connected(self) -> bool:
        """Return whether the router currently has an active SSH connection."""

        return (
            self.connection_manager is not None
            and self.connection_manager.connected
        )

    @classmethod
    def from_connection(
        cls,
        candidate: RouterCandidate,
        host_key_fingerprint: str,
    ) -> "Router":
        """Create a router from a verified SSH connection."""

        identity = RouterIdentity(
            mac_address=candidate.mac_address,
            ssh_host_key_fingerprint=host_key_fingerprint,
        )

        return cls(
            identity=identity,
            candidate=candidate,
        )
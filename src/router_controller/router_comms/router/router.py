"""Router device representation."""

from dataclasses import dataclass

from router_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
)
from router_controller.router_comms.router.identity import RouterIdentity


@dataclass
class Router:
    """A known router managed by the controller."""

    identity: RouterIdentity
    candidate: RouterCandidate

    name: str | None = None
    model: str | None = None
    architecture: str | None = None
    target: str | None = None
    firmware: str | None = None
"""Orchestration of router discovery and SSH provisioning."""

from __future__ import annotations

from typing import Callable

from openwrt_controller.router_comms.discovery.bootstrap import (
    RouterBootstrap,
)
from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterCandidate,
    RouterDiscovery,
)
from openwrt_controller.router_comms.ssh.connection import RouterConnection
from openwrt_controller.router_comms.ssh.key_installer import (
    RouterKeyInstaller,
)
from openwrt_controller.router_comms.ssh.keys import (
    SSHKeyManager,
    SSHKeyPair,
)


class RouterProvisioner:
    """Provision an OpenWrt router for controller SSH access.

    The provisioner coordinates the existing SSH components. It does not
    implement SSH itself and does not persist router state.
    """

    def __init__(
        self,
        key_manager: SSHKeyManager,
        discovery: RouterDiscovery,
        bootstrap_factory: Callable[[RouterCandidate], RouterBootstrap],
        connection_factory: Callable[
            [RouterCandidate, SSHKeyPair],
            RouterConnection,
        ],
    ) -> None:
        self.key_manager = key_manager
        self.discovery = discovery
        self.bootstrap_factory = bootstrap_factory
        self.connection_factory = connection_factory

    def provision(
        self,
        candidate: RouterCandidate | None = None,
    ) -> RouterCandidate:
        """Provision a router and verify key-based SSH authentication.

        If ``candidate`` is not supplied, discovery is performed.

        The controller key is loaded when it already exists. If no complete
        key pair exists, a new Ed25519 key pair is generated.

        Bootstrap communication is used only to install the controller's
        public key. The bootstrap connection is always closed before the
        permanent key-based connection is established.
        """

        key_pair = self._load_or_generate_key_pair()

        if candidate is None:
            candidate = self.discovery.discover()

        bootstrap = self.bootstrap_factory(candidate)
        client, _credentials = bootstrap.connect()

        try:
            installer = RouterKeyInstaller(client)
            installer.install(key_pair)
        finally:
            client.close()

        connection = self.connection_factory(candidate, key_pair)

        try:
            connection.connect()

            if not connection.connected:
                raise RuntimeError(
                    "Router SSH connection was not established."
                )
        finally:
            connection.close()

        return candidate

    def _load_or_generate_key_pair(self) -> SSHKeyPair:
        """Load the controller key pair or create it when absent."""

        try:
            return self.key_manager.load_key_pair()
        except FileNotFoundError:
            return self.key_manager.generate_key_pair()
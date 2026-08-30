"""Construction of router communication services."""

from future import annotations

from openwrt_controller.config import Config
from openwrt_controller.router_comms.discovery.bootstrap import (
    RouterBootstrap,
)
from openwrt_controller.router_comms.discovery.router_discovery import (
    RouterDiscovery,
)
from openwrt_controller.router_comms.provisioner import RouterProvisioner
from openwrt_controller.router_comms.ssh.connection import (
    RouterConnection,
    RouterConnectionConfig,
)
from openwrt_controller.router_comms.ssh.key_installer import (
    RouterKeyInstaller,
)
from openwrt_controller.router_comms.ssh.keys import SSHKeyManager

def create_router_provisioner(
        config_class: type[Config] = Config,
    ) -> RouterProvisioner:
        """Create the router provisioning service."""

    key_manager = SSHKeyManager(config_class.get_ssh_key_directory())

    discovery = RouterDiscovery(
        ssh_port=config_class.OPENWRT_SSH_PORT,
        timeout=config_class.OPENWRT_SSH_TIMEOUT,
    )

    return RouterProvisioner(
        key_manager=key_manager,
        discovery=discovery,
        bootstrap_factory=lambda candidate: RouterBootstrap(
            candidate=candidate,
            username=config_class.OPENWRT_SSH_USER,
            timeout=config_class.OPENWRT_SSH_TIMEOUT,
        ),
        installer_factory=lambda client: RouterKeyInstaller(client),
        connection_factory=lambda candidate, key_pair: RouterConnection(
            candidate=candidate,
            key_pair=key_pair,
            config=RouterConnectionConfig(
                username=config_class.OPENWRT_SSH_USER,
                timeout=config_class.OPENWRT_SSH_TIMEOUT,
            ),
        ),
    )
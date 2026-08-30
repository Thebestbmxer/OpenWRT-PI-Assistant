from .app import create_app
from .config import Config
from .router_comms.discovery.bootstrap import RouterBootstrap
from .router_comms.discovery.router_discovery import RouterCandidate
from .router_comms.discovery.router_discovery import RouterDiscovery
from .router_comms.provisioner import RouterProvisioner
from .router_comms.ssh.connection import RouterConnection
from .router_comms.ssh.connection import RouterConnectionConfig
from .router_comms.ssh.key_installer import RouterKeyInstaller
from .router_comms.ssh.keys import SSHKeyManager


app = create_app()


def provision_router() -> RouterCandidate:
    """Provision the configured OpenWrt router for SSH key access."""

    key_manager = SSHKeyManager(
        Config.get_ssh_key_directory()
    )

    discovery = RouterDiscovery(
        ssh_port=Config.OPENWRT_SSH_PORT,
        timeout=Config.OPENWRT_SSH_TIMEOUT,
    )

    def bootstrap_factory(candidate):
        return RouterBootstrap(
            candidate,
            username=Config.OPENWRT_SSH_USER,
            timeout=Config.OPENWRT_SSH_TIMEOUT,
        )

    def connection_factory(candidate, key_pair):
        return RouterConnection(
            candidate,
            key_pair,
            RouterConnectionConfig(
                username=Config.OPENWRT_SSH_USER,
                timeout=Config.OPENWRT_SSH_TIMEOUT,
            ),
        )

    provisioner = RouterProvisioner(
        key_manager=key_manager,
        discovery=discovery,
        bootstrap_factory=bootstrap_factory,
        installer_factory=RouterKeyInstaller,
        connection_factory=connection_factory,
    )

    return provisioner.provision()


def main():
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
    )


if __name__ == "__main__":
    main()

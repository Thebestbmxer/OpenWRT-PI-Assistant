from .app import create_app


app = create_app(
    provision_router=provision_router,
)


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


app = create_app(
    provision_router=provision_router,
)


def main():
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
    )


if __name__ == "__main__":
    main()

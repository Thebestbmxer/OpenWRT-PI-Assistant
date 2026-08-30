import logging

from flask import Flask

from .config import Config
from .database import initialize_database
from .logging_config import configure_logging
from .router_comms.discovery.bootstrap import RouterBootstrap
from .router_comms.discovery.router_discovery import RouterCandidate
from .router_comms.discovery.router_discovery import RouterDiscovery
from .router_comms.provisioner import RouterProvisioner
from .router_comms.ssh.connection import RouterConnection
from .router_comms.ssh.connection import RouterConnectionConfig
from .router_comms.ssh.key_installer import RouterKeyInstaller
from .router_comms.ssh.keys import SSHKeyManager
from .ui import register_routes


def _create_provision_router(config_class):
    """Create the router provisioning operation."""

    key_manager = SSHKeyManager(
        config_class.get_ssh_key_directory()
    )

    discovery = RouterDiscovery(
        ssh_port=config_class.OPENWRT_SSH_PORT,
        timeout=config_class.OPENWRT_SSH_TIMEOUT,
    )

    def bootstrap_factory(candidate: RouterCandidate):
        return RouterBootstrap(
            candidate,
            username=config_class.OPENWRT_SSH_USER,
            timeout=config_class.OPENWRT_SSH_TIMEOUT,
        )

    def connection_factory(candidate, key_pair):
        return RouterConnection(
            candidate,
            key_pair,
            RouterConnectionConfig(
                username=config_class.OPENWRT_SSH_USER,
                timeout=config_class.OPENWRT_SSH_TIMEOUT,
            ),
        )

    provisioner = RouterProvisioner(
        key_manager=key_manager,
        discovery=discovery,
        bootstrap_factory=bootstrap_factory,
        installer_factory=RouterKeyInstaller,
        connection_factory=connection_factory,
    )

    return provisioner.provision


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    configure_logging(config_class)

    logger = logging.getLogger(__name__)
    logger.info("Starting OpenWrt Pi Controller")

    app = Flask(__name__)

    app.config.from_object(config_class)

    initialize_database(config_class)

    provision_router = _create_provision_router(config_class)

    register_routes(
        app,
        provision_router,
    )

    return app

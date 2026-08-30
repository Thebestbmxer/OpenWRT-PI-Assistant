import logging

from flask import Flask

from .config import Config
from .database import initialize_database
from .logging_config import configure_logging
from .router_comms.factory import create_router_provisioner
from .ui import register_routes

def create_app(config_class=Config, provision_router=None):
    """Create and configure the Flask application."""

    configure_logging(config_class)

    logger = logging.getLogger(__name__)
    logger.info("Starting OpenWrt Pi Controller")

    app = Flask(__name__)

    app.config.from_object(config_class)

    initialize_database(config_class)

    if provision_router is None:
        provisioner = create_router_provisioner(config_class)
        provision_router = provisioner.provision

    register_routes(app, provision_router)

    return app
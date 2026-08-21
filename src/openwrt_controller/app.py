import logging

from flask import Flask

from .config import Config
from .database import initialize_database
from .logging_config import configure_logging

def create_app(config_class=Config):
    """Create and configure the Flask application."""

    configure_logging(config_class)

    logger = logging.getLogger(__name__)
    logger.info("Starting OpenWrt Pi Controller")

    app = Flask(__name__)

    app.config.from_object(config_class)

    initialize_database(config_class)

    @app.route("/")
    def index():
        return "OpenWrt Pi Controller"

    return app

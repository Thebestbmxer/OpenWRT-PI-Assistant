from flask import Flask

from .config import Config
from .database import initialize_database

def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(__name__)

    app.config.from_object(config_class)

    initialize_database(config_class)

    @app.route("/")
    def index():
        return "OpenWrt Pi Controller"

    return app

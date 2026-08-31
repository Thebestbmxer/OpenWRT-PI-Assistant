import os
from pathlib import Path


class Config:
    """Application configuration."""

    # Application
    APP_NAME = "Router Pi Controller"
    APP_VERSION = "0.1.0"
    DEBUG = False

    APPLICATION_USER = os.getenv(
    "ROUTER_CONTROLLER_USER",
    "router_controller",
    )

    # Paths
    @classmethod
    def get_data_dir(cls):
        return Path(
            os.getenv(
                "ROUTER_CONTROLLER_DATA_DIR",
                "/var/lib/router-pi-controller",
            )
        )

    @classmethod
    def get_database_path(cls):
        return cls.get_data_dir() / "controller.db"
    
    @classmethod
    def get_ssh_key_directory(cls):
        return cls.get_data_dir() / ".ssh"
    
    @classmethod
    def get_ssh_private_key_path(cls):
        return cls.get_ssh_key_directory() / "controller"

    @classmethod
    def get_ssh_public_key_path(cls):
        return cls.get_ssh_key_directory() / "controller.pub"

    # Web application
    HOST = os.getenv("ROUTER_CONTROLLER_HOST", "0.0.0.0")
    PORT = int(os.getenv("ROUTER_CONTROLLER_PORT", "8080"))

    # Router SSH connection
    ROUTER_HOST = os.getenv(
        "ROUTER_CONTROLLER_ROUTER_HOST",
        "192.168.1.1",
    )

    ROUTER_SSH_PORT = int(
        os.getenv("ROUTER_CONTROLLER_ROUTER_PORT", "22")
    )

    ROUTER_SSH_USER = os.getenv(
        "ROUTER_CONTROLLER_ROUTER_USER",
        "root",
    )

    ROUTER_SSH_TIMEOUT = int(
        os.getenv("ROUTER_CONTROLLER_SSH_TIMEOUT", "10")
    )
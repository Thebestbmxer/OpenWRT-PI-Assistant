import os
from pathlib import Path


class Config:
    """Application configuration."""

    # Application
    APP_NAME = "OpenWrt Pi Controller"
    APP_VERSION = "0.1.0"
    DEBUG = False

    APPLICATION_USER = os.getenv(
    "OPENWRT_CONTROLLER_USER",
    "openwrt-controller",
    )

    # Paths
    DATA_DIR = Path(
        os.getenv(
            "OPENWRT_CONTROLLER_DATA_DIR",
            "/var/lib/openwrt-pi-controller",
        )
    )

    DATABASE_PATH = DATA_DIR / "controller.db"

    # Web application
    HOST = os.getenv("OPENWRT_CONTROLLER_HOST", "0.0.0.0")
    PORT = int(os.getenv("OPENWRT_CONTROLLER_PORT", "8080"))

    # OpenWrt SSH connection
    OPENWRT_HOST = os.getenv(
        "OPENWRT_CONTROLLER_ROUTER_HOST",
        "192.168.1.1",
    )

    OPENWRT_SSH_PORT = int(
        os.getenv("OPENWRT_CONTROLLER_ROUTER_PORT", "22")
    )

    OPENWRT_SSH_USER = os.getenv(
        "OPENWRT_CONTROLLER_ROUTER_USER",
        "root",
    )

    OPENWRT_SSH_TIMEOUT = int(
        os.getenv("OPENWRT_CONTROLLER_SSH_TIMEOUT", "10")
    )

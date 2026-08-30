"""Web UI for the OpenWrt Pi Controller."""

from flask import Flask

from .home import register_home_routes
from .router import register_router_routes
from .test_page import register_routes

__version__ = "0.0.1"

def register_routes(app: Flask, provision_router) -> None:
    register_home_routes(app)
    register_router_routes(app, provision_router)

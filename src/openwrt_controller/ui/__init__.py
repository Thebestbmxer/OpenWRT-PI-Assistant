"""Web UI for the OpenWrt Pi Controller."""

version = "0.0.2"

from flask import Flask

def register_ui_context(app: Flask) -> None:
    """Register values available to all UI templates."""

@app.context_processor
def inject_ui_version():
    return {
        "ui_version": __version__,
    }


from .welcome import register_routes

all = [
    "register_routes",
    "register_ui_context",
    "version",
]
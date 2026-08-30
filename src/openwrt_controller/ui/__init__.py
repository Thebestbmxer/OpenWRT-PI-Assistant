"""Web UI for the OpenWrt Pi Controller."""

__version__ = "0.1"

from flask import Flask

from .home import register_routes


def register_ui_context(app: Flask) -> None:
    """Register values available to all UI templates."""

    @app.context_processor
    def inject_ui_context() -> dict[str, str]:
        """Provide common UI values to templates."""

        return {
            "ui_version": __version__,
        }

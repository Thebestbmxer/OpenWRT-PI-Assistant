"""Web UI for the Router Pi Controller."""

__version__ = "0.2"

from flask import Flask

from .welcome import register_routes

def register_ui_context(app: Flask) -> None:
    """Register values available to all UI templates."""

    @app.context_processor
    def inject_ui_context() -> dict[str, str]:
        """Provide common UI values to templates."""

        return {"ui_version": __version__,}

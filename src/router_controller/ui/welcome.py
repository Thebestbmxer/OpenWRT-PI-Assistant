import logging

from flask import jsonify, render_template

from router_controller.router_comms.discovery.initial_connection import (
    discover_and_connect_router,
)

logger = logging.getLogger(__name__)


def register_routes(app, provision_router):
    """Register the router provisioning welcome page."""

    @app.route("/")
    def index():
        return render_template("welcome.html")

    @app.get("/api/router/discover")
    def discover_router_endpoint():
        """Discover a router and check initial SSH communication."""

        logger.info(
            "Router discovery requested from web interface"
        )

        try:
            result = discover_and_connect_router()

            if result.candidate is None:
                return jsonify(
                    {
                        "found": False,
                        "connected": False,
                        "error": str(result.error)
                        if result.error
                        else "No router was discovered.",
                    }
                ), 404

            response = {
                "found": True,
                "connected": result.connected,
                "address": result.candidate.address,
                "ssh_port": result.candidate.ssh_port,
            }

            if result.error is not None:
                response["error"] = str(result.error)

            return jsonify(response)

        except Exception as exc:
            logger.exception(
                "Router discovery and initial connection failed"
            )

            return jsonify(
                {
                    "found": False,
                    "connected": False,
                    "error": str(exc),
                }
            ), 500

    @app.post("/api/router/provision")
    def provision_router_endpoint():
        """Install and verify the controller SSH key."""

        logger.info(
            "Router provisioning requested from web interface"
        )

        if provision_router is None:
            return jsonify(
                {"error": "Router provisioning is not configured."}
            ), 503

        try:
            candidate = provision_router()

            return jsonify(
                {
                    "success": True,
                    "address": candidate.address,
                    "ssh_port": candidate.ssh_port,
                    "message": (
                        "SSH key installed and keyed SSH connection "
                        "verified."
                    ),
                }
            )

        except Exception as exc:
            logger.exception("Router provisioning failed")

            return jsonify(
                {
                    "success": False,
                    "error": str(exc),
                }
            ), 500

import logging

from flask import Flask, jsonify

logger = logging.getLogger(__name__)


def register_router_routes(app: Flask, provision_router) -> None:
    @app.route("/api/router/provision", methods=["POST"])
    def provision_router_endpoint():
        logger.info(
            "Router provisioning requested from web interface"
        )

        try:
            candidate = provision_router()

            return jsonify(
                {
                    "status": "success",
                    "address": candidate.address,
                    "ssh_port": candidate.ssh_port,
                }
            )

        except Exception as exc:
            logger.exception("Router provisioning failed")

            return jsonify(
                {
                    "status": "error",
                    "error": str(exc),
                }
            ), 500

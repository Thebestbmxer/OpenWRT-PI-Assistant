import logging

from flask import jsonify, render_template

logger = logging.getLogger(__name__)

def register_routes(app, provision_router):
    """Register the router provisioning welcome page."""

#@app.route("/")
#def index():
#    return render_template("welcome.html")

@app.get("/api/router/discover")
def discover_router_endpoint():
    """Discover an OpenWrt router without modifying it."""

    logger.info(
        "Router discovery requested from web interface"
    )

    if provision_router is None:
        return jsonify(
            {"error": "Router provisioning is not configured."}
        ), 503

    try:
        candidate = provision_router.discovery.discover()

        return jsonify(
            {
                "found": True,
                "address": candidate.address,
                "ssh_port": candidate.ssh_port,
            }
        )

    except Exception as exc:
        logger.exception("Router discovery failed")

        return jsonify(
            {
                "found": False,
                "error": str(exc),
            }
        ), 404

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
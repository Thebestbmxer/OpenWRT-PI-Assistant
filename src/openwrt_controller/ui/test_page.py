from flask import Flask

def register_routes(app: Flask) -> None:
    """Register web UI routes on the Flask application."""

    @app.route("/")
    def index():
        return render_template_string(
            """
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>OpenWrt Pi Controller</title>
                <style>
                    body {
                        font-family: sans-serif;
                        max-width: 700px;
                        margin: 40px auto;
                        padding: 0 20px;
                    }

                    button {
                        padding: 12px 20px;
                        font-size: 16px;
                        cursor: pointer;
                    }

                    #status {
                        margin-top: 20px;
                        white-space: pre-wrap;
                    }
                </style>
            </head>
            <body>
                <h1>OpenWrt Pi Controller</h1>

                <button id="provision-button">
                    Install Router SSH Key
                </button>

                <div id="status"></div>

                <script>
                    const button = document.getElementById(
                        "provision-button"
                    );
                    const status = document.getElementById("status");

                    button.addEventListener("click", async () => {
                        button.disabled = true;
                        status.textContent =
                            "Discovering router and installing SSH key...";

                        try {
                            const response = await fetch(
                                "/api/router/provision",
                                {
                                    method: "POST"
                                }
                            );

                            const result = await response.json();

                            if (!response.ok) {
                                throw new Error(
                                    result.error || "Provisioning failed."
                                );
                            }

                            status.textContent =
                                "Success. Router discovered at " +
                                result.address +
                                ":" +
                                result.ssh_port;
                        } catch (error) {
                            status.textContent =
                                "Error: " + error.message;
                        } finally {
                            button.disabled = false;
                        }
                    });
                </script>
            </body>
            </html>
            """
        )

    @app.post("/api/router/provision")
    def provision_router_endpoint():
        """Discover and provision an OpenWrt router."""

        logger.info("Router provisioning requested from web interface")

        try:
            # Import here to avoid introducing an application import cycle.
            from .main import provision_router

            candidate = provision_router()

            logger.info(
                "Router provisioning completed successfully: %s:%s",
                candidate.address,
                candidate.ssh_port,
            )

            return jsonify(
                {
                    "success": True,
                    "address": candidate.address,
                    "ssh_port": candidate.ssh_port,
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

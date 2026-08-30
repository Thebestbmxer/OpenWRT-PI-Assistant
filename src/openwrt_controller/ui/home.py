from flask import Flask, render_template


def register_home_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        return render_template("home.html")

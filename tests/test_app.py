from openwrt_controller.app import create_app


def test_create_app():
    app = create_app()

    assert app is not None
    assert app.config["HOST"] == "127.0.0.1"
    assert app.config["PORT"] == 8080


def test_index():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.data == b"OpenWrt Pi Controller"
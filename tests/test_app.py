import sqlite3

from openwrt_controller.app import create_app

def test_create_app():
    app = create_app()

    assert app is not None
    assert app.config["HOST"] == "0.0.0.0"
    assert app.config["PORT"] == 8080


def test_index():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.data == b"OpenWrt Pi Controller"

    def test_create_app_initializes_database(tmp_path):
    class TestConfig:
        HOST = "127.0.0.1"
        PORT = 8080
        DATA_DIR = tmp_path
        DATABASE_PATH = tmp_path / "controller.db"

    create_app(TestConfig)

    assert TestConfig.DATABASE_PATH.exists()

    connection = sqlite3.connect(TestConfig.DATABASE_PATH)

    try:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

    finally:
        connection.close()

    table_names = {row[0] for row in tables}

    assert "devices" in table_names
    assert "events" in table_names
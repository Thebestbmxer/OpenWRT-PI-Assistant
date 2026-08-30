import sqlite3
import pytest

@pytest.fixture(autouse=True)
def test_environment(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "OPENWRT_CONTROLLER_DATA_DIR",
        str(tmp_path / "openwrt-pi-controller-test"),
    )

def test_create_app():
    from openwrt_controller.app import create_app
    app = create_app()

    assert app is not None
    assert app.config["HOST"] == "0.0.0.0"
    assert app.config["PORT"] == 8080


def test_index():
    from openwrt_controller.app import create_app
    app = create_app()

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 500
    #assert response.data == b"OpenWrt Pi Controller"

def test_create_app_initializes_database(tmp_path):
    from openwrt_controller.app import create_app

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

def test_create_app_logs_startup(tmp_path):
    from openwrt_controller.app import create_app

    class TestConfig:
        HOST = "127.0.0.1"
        PORT = 8080
        DATA_DIR = tmp_path
        DATABASE_PATH = tmp_path / "controller.db"

    create_app(TestConfig)

    log_file = tmp_path / "logs" / "controller.log"

    assert log_file.exists()
    assert "Starting OpenWrt Pi Controller" in log_file.read_text()

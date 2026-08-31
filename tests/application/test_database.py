from pathlib import Path
import sqlite3

from router_controller.database import initialize_database


def test_initialize_database(tmp_path):
    class TemporaryConfig:
        DATA_DIR = tmp_path
        DATABASE_PATH = tmp_path / "controller.db"

    initialize_database(TemporaryConfig)

    database_path = Path(TemporaryConfig.DATABASE_PATH)

    assert database_path.exists()

    connection = sqlite3.connect(database_path)

    try:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()

    table_names = {row[0] for row in tables}

    assert "devices" in table_names
    assert "events" in table_names
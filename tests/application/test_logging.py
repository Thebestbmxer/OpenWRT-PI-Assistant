from pathlib import Path

from router_controller.logging_config import configure_logging


def test_configure_logging(tmp_path):
    class TestConfig:
        DATA_DIR = tmp_path

    logger = configure_logging(TestConfig)

    logger.info("test log message")

    log_file = Path(tmp_path) / "logs" / "controller.log"

    assert log_file.exists()
    assert "test log message" in log_file.read_text()

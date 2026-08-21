import logging
from pathlib import Path

from .config import Config


def configure_logging(config=Config):
    """Configure application logging."""

    log_directory = Path(config.DATA_DIR) / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file = log_directory / "controller.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
        force=True,
    )

    return logging.getLogger("openwrt_controller")
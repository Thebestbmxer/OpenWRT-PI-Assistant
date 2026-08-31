import logging
from pathlib import Path

from .config import Config


def configure_logging(config=Config):
    """Configure application logging."""

    if hasattr(config, "get_data_dir"):
        data_dir = config.get_data_dir()
    else:
        data_dir = config.DATA_DIR

    log_directory = Path(data_dir) / "logs"
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

    return logging.getLogger("router_controller")
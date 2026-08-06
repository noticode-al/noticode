import logging
from pathlib import Path

from packages.core.config import AppConfig


def configure_logging(config: AppConfig) -> logging.Logger:
    """Noticode için konsol ve dosya loglamasını yapılandırır."""

    log_directory = config.data_directory / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(config.app_name.lower())
    logger.setLevel(config.log_level.upper())
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        Path(log_directory) / "noticode.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

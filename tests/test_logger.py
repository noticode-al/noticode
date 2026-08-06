import logging
from pathlib import Path

from packages.core.config import AppConfig
from packages.core.logger import configure_logging


def test_configure_logging_creates_log_directory(tmp_path: Path) -> None:
    config = AppConfig(
        data_directory=tmp_path,
        log_level="INFO",
    )

    logger = configure_logging(config)

    assert (tmp_path / "logs").exists()
    assert logger.name == "noticode"
    assert logger.level == logging.INFO


def test_configure_logging_adds_console_and_file_handlers(
    tmp_path: Path,
) -> None:
    config = AppConfig(
        app_name="NoticodeLoggerTest",
        data_directory=tmp_path,
        log_level="DEBUG",
    )

    logger = configure_logging(config)

    handler_types = {type(handler) for handler in logger.handlers}

    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types
    assert logger.level == logging.DEBUG


def test_logger_writes_message_to_file(tmp_path: Path) -> None:
    config = AppConfig(
        app_name="NoticodeFileLoggerTest",
        data_directory=tmp_path,
        log_level="INFO",
    )

    logger = configure_logging(config)
    logger.info("Test log mesajı.")

    for handler in logger.handlers:
        handler.flush()

    log_file = tmp_path / "logs" / "noticode.log"

    assert log_file.exists()
    assert "Test log mesajı." in log_file.read_text(encoding="utf-8")


def test_configure_logging_does_not_duplicate_handlers(
    tmp_path: Path,
) -> None:
    config = AppConfig(
        app_name="NoticodeDuplicateLoggerTest",
        data_directory=tmp_path,
        log_level="INFO",
    )

    first_logger = configure_logging(config)
    first_handler_count = len(first_logger.handlers)

    second_logger = configure_logging(config)

    assert first_logger is second_logger
    assert len(second_logger.handlers) == first_handler_count

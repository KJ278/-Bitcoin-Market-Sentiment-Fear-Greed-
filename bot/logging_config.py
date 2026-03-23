"""Logging configuration helpers."""

from __future__ import annotations

import logging
from pathlib import Path

DEFAULT_LOG_FILE = "logs/trading_bot.log"


def setup_logger(log_file: str = DEFAULT_LOG_FILE) -> logging.Logger:
    """Configure and return the app logger."""
    logger = logging.getLogger("trading_bot")
    if logger.handlers:
        return logger

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger

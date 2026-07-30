import logging
import os
import sys
from typing import Optional, Union
from rich.logging import RichHandler


def setup_logger(
    name: str = "GenAI",
    level: Optional[Union[str, int]] = None,
    log_file: Optional[str] = "genai.log",
) -> logging.Logger:
    if level is None:
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_str, logging.INFO)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_path=False,
    )
    console_handler.setLevel(level)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(filename)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            sys.stderr.write(f"Failed to setup file handler for logger: {e}\n")

    logger.propagate = False
    return logger


def get_logger(name: str = "GenAI") -> logging.Logger:
    return setup_logger(name)


logger = get_logger("GenAI")

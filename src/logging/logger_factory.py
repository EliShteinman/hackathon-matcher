import logging
import sys

from config.logging_settings import LoggingSettings


def setup_logging(settings: LoggingSettings) -> logging.Logger:
    root_logger = logging.getLogger("hackathon_matcher")
    root_logger.setLevel(getattr(logging, settings.level.upper(), logging.INFO))

    formatter = logging.Formatter(settings.format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if settings.file_path:
        file_handler = logging.FileHandler(settings.file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger

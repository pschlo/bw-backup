from __future__ import annotations

import logging
import sys

HANDLER_NAME = "bw-backup"


def setup_logging(
    root_loglevel: int = logging.INFO,
    include_packages: set[str] | None = None,
    others_loglevel: int = logging.WARNING,
) -> None:
    """Configure console logging for the command-line application."""
    included = set(include_packages or ())
    included |= {"__main__", __name__.split(".")[0]}

    for logger in _known_loggers():
        if logger.name.split(".")[0] not in included:
            logger.setLevel(others_loglevel)

    _setup_root_logger(root_loglevel)


def _known_loggers() -> set[logging.Logger]:
    return {
        logger
        for logger in logging.root.manager.loggerDict.values()
        if isinstance(logger, logging.Logger)
    }


def _setup_root_logger(loglevel: int) -> None:
    logger = logging.getLogger()
    logger.setLevel(loglevel)

    if not any(handler.get_name() == HANDLER_NAME for handler in logger.handlers):
        formatter = logging.Formatter("[%(asctime)s %(levelname)s]: %(message)s", "%H:%M:%S")
        stream_handler = logging.StreamHandler()
        stream_handler.set_name(HANDLER_NAME)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logging.addLevelName(logging.DEBUG, "DBUG")
    logging.addLevelName(logging.INFO, "INFO")
    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.ERROR, " ERR")
    logging.addLevelName(logging.CRITICAL, "CRIT")

    def handle_exception(exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            logger.info("Keyboard interrupt")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

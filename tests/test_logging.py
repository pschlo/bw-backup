from __future__ import annotations

import logging
import sys

from bw_backup.setup_logging import HANDLER_NAME, setup_logging


def test_setup_logging_does_not_duplicate_its_handler() -> None:
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    original_excepthook = sys.excepthook

    try:
        setup_logging()
        setup_logging()
        matching_handlers = [
            handler for handler in root_logger.handlers if handler.get_name() == HANDLER_NAME
        ]
        assert len(matching_handlers) == 1
    finally:
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)
        sys.excepthook = original_excepthook

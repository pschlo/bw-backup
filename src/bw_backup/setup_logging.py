import logging
import sys


def setup_logging(root_loglevel: int = logging.INFO, include_packages: set[str]|None = None, others_loglevel: int = logging.WARNING):
    """
    - sets log level of the root logger
    - sets log level for logger of other (i.e. not included) packages
    - configures the root logger
    """
    if include_packages is None:
        include_packages = set()
    include_packages |= {'__main__', __name__.split('.')[0]}  # executed script and current package are always included

    loggers = {logging.getLogger(name) for name in logging.root.manager.loggerDict}

    for logger in loggers:
        if logger.name.split('.')[0] not in include_packages:
            logger.setLevel(others_loglevel)
    
    _setup_root_logger(root_loglevel)


def _setup_root_logger(loglevel: int):
    """Configures the root logger with formatter, handlers, and exception handling."""
    logger = logging.getLogger()
    logger.setLevel(loglevel)

    # configure formatter
    formatter = logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s', '%H:%M:%S')

    # configure stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # configure level names
    logging.addLevelName(logging.DEBUG, 'DBUG')
    logging.addLevelName(logging.INFO, 'INFO')
    logging.addLevelName(logging.WARNING, 'WARN')
    logging.addLevelName(logging.ERROR, ' ERR')
    logging.addLevelName(logging.CRITICAL, 'CRIT')

    # log uncaught errors
    # see https://stackoverflow.com/a/16993115
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            logger.info('Keyboard interrupt')
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

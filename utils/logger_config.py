import logging
import logging.handlers

LOG_FORMAT = "%(asctime)s — %(levelname)s — %(filename)s — %(funcName)s:%(lineno)d — %(message)s"
LOG_LEVEL = logging.INFO

LOG_FILE = "C:\\opt\\essential-metrics\\essential-metrics.log"

def configure_logger(name, log_level=LOG_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=5, delay=True)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
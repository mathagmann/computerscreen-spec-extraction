from loguru import logger

from config import LOG_DIR

default_log = dict(
    sink=LOG_DIR / "root.log",
    rotation="1 week",
    retention="1 month",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)


def setup_logging():
    """Configure logging to file and console."""
    logger.add(**default_log)
    return logger


setup_logging()

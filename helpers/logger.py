import logging
import sys

def get_logger(name: str = "test_framework"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARN)

    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

logger = get_logger()
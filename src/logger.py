import logging
import sys


def configure_logger(name):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("root")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


logger = configure_logger("root")
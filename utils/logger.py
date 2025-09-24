# utils/logger.py

import logging

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def log_info(message: str):
    logging.info(message)


def log_error(message: str):
    logging.error(message)

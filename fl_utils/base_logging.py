import os
import logging
from typing import Optional
from logging.handlers import RotatingFileHandler
LOG_PATH = "/data/FaceLock/logs/"
os.makedirs(LOG_PATH, exist_ok=True)
import sys

def setup_logging(
        file_name: Optional[str] = "face_lock.log",
        logger: logging.Logger = None,
):
    formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - [%(name)s]: %(message)s')
    if not logger:
        logger = logging.getLogger()

    if file_name:
        # write more logs on servers development
        rh = RotatingFileHandler(
            filename=f"{LOG_PATH}{file_name}"
        )
        rh.setLevel(logging.DEBUG)
        rh.setFormatter(formatter)
        logger.addHandler(rh)


    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.setLevel(logging.DEBUG)
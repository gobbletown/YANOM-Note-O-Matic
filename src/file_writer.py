from io import BytesIO
import logging
from pathlib import Path

import config

logger = logging.getLogger(f'{config.APP_NAME}.{__name__}')
logger.setLevel(config.logger_level)


def store_file(absolute_path, content_to_save):

    logger.debug(f"Storing attachment {absolute_path}")
    if isinstance(content_to_save, str):
        write_text(absolute_path, content_to_save)
        return

    if isinstance(content_to_save, bytes):
        write_bytes(absolute_path, content_to_save)
        return

    if isinstance(content_to_save, BytesIO):
        write_bytes_IO(absolute_path, content_to_save)
        return

    logger.warning(f"content type {type(content_to_save)} was not recognised for path {absolute_path}")


def write_text(absolute_path, content_to_save):
    try:
        Path(absolute_path).write_text(content_to_save, encoding="utf-8")
    except FileNotFoundError as e:
        logger.error(f"{e}")


def write_bytes(absolute_path, content_to_save):
    try:
        Path(absolute_path).write_bytes(content_to_save)
    except FileNotFoundError as e:
        logger.error(f"{e}")


def write_bytes_IO(absolute_path, content_to_save):
    try:
        Path(absolute_path).write_bytes(content_to_save.getbuffer())
    except FileNotFoundError as e:
        logger.error(f"{e}")
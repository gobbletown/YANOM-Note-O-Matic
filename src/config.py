APP_NAME = 'YANOM'
APP_SUB_NAME = 'Note-O-Matic'
VERSION = 1.0
DATA_DIR = 'data'
global logger_level
logger_level = 20  # INFO


def set_logger_level(level: int):
    global logger_level
    logger_level = level

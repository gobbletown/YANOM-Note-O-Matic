APP_NAME = 'YANOM'
APP_SUB_NAME = 'Note-O-Matic'
VERSION = '1.1.0'
DATA_DIR = 'data'
global logger_level
logger_level = 20  # INFO
global silent
silent = False
global ini
ini = False


def set_logger_level(level: int):
    global logger_level
    logger_level = level


def set_silent(silent_mode: bool):
    global silent
    silent = silent_mode


def set_ini(use_ini: bool):
    global ini
    ini = use_ini
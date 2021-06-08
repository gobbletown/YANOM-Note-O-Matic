#!/usr/bin/env python3
""" Parse command line arguments, configure root loggers and initialise the note conversion process """
import logging.handlers as handlers
import os

import argparse
import logging
import sys

import config
from config_data import ConfigData
from helper_functions import find_working_directory
from notes_converter import NotesConvertor


def what_module_is_this():
    return __name__


def command_line_parser(args):
    parser = argparse.ArgumentParser(description="YANOM Note-O-Matic notes convertor")

    parser.add_argument('-v', '--version', action='version', version='%(prog)s Version {}'.format(config.VERSION))
    parser.add_argument("-s", "--silent", action="store_true",
                        help="No output to console. WILL also use ini file settings.")
    parser.add_argument('--source', nargs='?', default='',
                        help='Sub directory of "data" directory containing one or more files to process, '
                             'or the name of a single file.  '
                             'For example "--source my_html_file.html" or "--source my_nsx_files"  '
                             'If not provided will search and use data folder AND any sub folders.'
                             'When --source is provided it WILL override config.ini setting when '
                             'used with the -i option')
    parser.add_argument("-l", "--log", default='INFO',
                        help="Set the level of program logging. Default = INFO. "
                             "Choices are INFO, DEBUG, WARNING, ERROR, CRITICAL"
                             "Example --log debug or --log INFO")
    group = parser.add_argument_group('Mutually exclusive options. ',
                                      'To use the interactive command line tool for settings '
                                      'DO NOT use -s or -i')
    settings_from_group = group.add_mutually_exclusive_group()
    settings_from_group.add_argument("-i", "--ini", action="store_true",
                                     help="Use config.ini for conversion settings.")
    settings_from_group.add_argument("-c", "--cli", action="store_true",
                                     help="Use interactive command line interface to choose options and settings. "
                                          "This is the default if no argument is provided.")

    return vars(parser.parse_args(args))


def set_logging_level(log_level: str):
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    new_level = levels.get(log_level.lower(), None)

    if new_level is None:
        try:
            raise ValueError(f'Invalid log level on command line: "{log_level}"')
        except Exception as exc:
            sys.exit(exc)

    config.set_logger_level(new_level)
    pass


def setup_logging(working_path):
    os.makedirs(f"{working_path}/{config.DATA_DIR}/logs", exist_ok=True)

    log_filename = f"{working_path}/{config.DATA_DIR}/logs/normal.log"
    error_log_filename = f"{working_path}/{config.DATA_DIR}/logs/error.log"
    debug_log_filename = f"{working_path}/{config.DATA_DIR}/logs/debug.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logHandler = handlers.RotatingFileHandler(log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(file_formatter)

    errorLogHandler = handlers.RotatingFileHandler(error_log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
    errorLogHandler.setLevel(logging.ERROR)
    errorLogHandler.setFormatter(file_formatter)

    if config.logger_level == logging.DEBUG:
        debugLogHandler = handlers.RotatingFileHandler(debug_log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
        debugLogHandler.setLevel(logging.DEBUG)
        debugLogHandler.setFormatter(file_formatter)
        root_logger.addHandler(debugLogHandler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(logHandler)
    root_logger.addHandler(errorLogHandler)


def main(command_line_sys_argv=sys.argv):
    args = command_line_parser(command_line_sys_argv[1:])
    set_logging_level(args['log'])
    config.set_silent(args['silent'])
    working_directory, working_directory_message = find_working_directory()
    setup_logging(working_directory)
    logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}')
    logger.debug(working_directory_message)
    return args


if __name__ == '__main__':
    command_line_args = main()
    config_data = ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    config_data.parse_config_file()
    notes_converter = NotesConvertor(command_line_args, config_data)
    notes_converter.convert_notes()

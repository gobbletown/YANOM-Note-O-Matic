import logging
from pathlib import Path

import config
import helper_functions

logger = logging.getLogger(f'{config.APP_NAME}.{__name__}')
logger.setLevel(config.logger_level)


def store_file(file_path, content):
    try:
        Path(file_path).write_text(content, 'utf-8')
    except FileNotFoundError:
        logger.error(f"Failed to write content to {file_path}")
        if not config.silent:
            print(f"Failed to write content to {file_path}")


def generate_output_path(title: str, folder_name, conversion_settings):
    dirty_filename = __append_file_extension(title, conversion_settings.export_format)
    clean_filename = __clean_filename(dirty_filename)
    valid_path_for_file = __generate_valid_output_path(conversion_settings, folder_name, clean_filename)
    return valid_path_for_file


def __append_file_extension(title, export_format):
    if export_format == 'html':
        return f"{title}.html"

    return f"{title}.md"


def __clean_filename(dirty_filename):
    clean_filename = helper_functions.generate_clean_path(dirty_filename)
    return clean_filename


def __generate_valid_output_path(conversion_settings, folder_name, filename):
    path_to_file = Path(conversion_settings.working_directory, config.DATA_DIR,
                        conversion_settings.export_folder_name, folder_name, filename)

    valid_file_path = helper_functions.find_valid_full_file_path(path_to_file)

    return valid_file_path

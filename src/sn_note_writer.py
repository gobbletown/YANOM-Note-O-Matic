import logging
import sys
from pathlib import Path

import config
from helper_functions import generate_clean_path, find_working_directory


def what_module_is_this():
    return __name__


class NoteWriter:
    def __init__(self, conversion_settings):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self.conversion_settings = conversion_settings
        self.working_directory = conversion_settings.working_directory
        self.output_folder = conversion_settings.export_folder_name
        self.output_full_path = None
        self.output_file_name = None


    def store_file(self, note_page):
        self.logger.debug(f"Storing note '{note_page.title}' as '{note_page.file_name}' "
                          f"in notebook folder '{note_page.notebook_folder_name}'")
        try:
            Path(note_page.full_path).write_text(note_page.converted_content, 'utf-8')
        except Exception as e:
            self.logger.error(f"Failed to write note '{note_page.title}' as '{note_page.file_name}' "
                              f"in notebook folder '{note_page.notebook_folder_name}'\n {str(e)}")
            if not config.silent:
                print(f"Failed to note '{note_page.title}' as '{note_page.file_name}' "
                      f"in notebook folder '{note_page.notebook_folder_name}'\n {str(e)} ")
            sys.exit(0)

    def generate_output_path_and_set_note_file_name(self, note_page):
        self.logger.debug(f"Generate output path for '{note_page.title}'")
        dirty_filename = note_page.title

        if self.conversion_settings.creation_time_in_exported_file_name:
            dirty_filename = f"{note_page.note_json['ctime']}-{dirty_filename}"

        if self.conversion_settings.export_format == 'html':
            dirty_filename = f"{dirty_filename}.html"
        else:
            dirty_filename = f"{dirty_filename}.md"

        self.output_file_name = (generate_clean_path(dirty_filename))
        n = 0
        target_path = Path(self.working_directory, config.DATA_DIR, self.output_folder,
                           note_page.notebook_folder_name, self.output_file_name)
        while target_path.exists():
            n += 1
            target_path = Path(self.working_directory, config.DATA_DIR, self.output_folder,
                               note_page.notebook_folder_name,
                               f"{Path(self.output_file_name).stem}-{n}{Path(self.output_file_name).suffix}")

        self.output_file_name = target_path.name
        self.output_full_path = target_path
        self.logger.debug(
            f"Path for '{note_page.title}' is {self.output_full_path}, file name will be {self.output_file_name}")

    def get_output_full_path(self):
        return self.output_full_path

    def get_output_file_name(self):
        return self.output_file_name

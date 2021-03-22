#!/usr/bin/env python
import sys
import inspect
import logging
import logging.handlers as handlers
from nsx_file_converter import NSXFile
from config_data import ConfigData
from globals import APP_NAME
from interactive_cli import StartUpCommandLineInterface
from arg_parsing import CommandLineParsing
import quick_settings
from timer import Timer
from quick_settings import ConversionSettings
from html_file_converter import HTMLConverter


log_filename = 'normal.log'
error_log_filename = 'error.log'

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

logHandler = handlers.RotatingFileHandler(log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(file_formatter)

errorLogHandler = handlers.RotatingFileHandler(error_log_filename, maxBytes=2 * 1024 * 1024, backupCount=5)
errorLogHandler.setLevel(logging.ERROR)
errorLogHandler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.CRITICAL)

root_logger.addHandler(logHandler)
root_logger.addHandler(errorLogHandler)
root_logger.addHandler(console_handler)


class ConfigException(Exception):
    pass


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_module_is_this():
    return __name__


def what_class_is_this(obj):
    return obj.__class__.__name__


class NotesConvertor:
    """
    A class to intialise and organise the conversion of notes files into alternative output formats
    """

    def __init__(self):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.info(f'{what_method_is_this()} - Program startup')
        self._note_page_count = 0
        self._note_book_count = 0
        self._image_count = 0
        self._attachment_count = 0
        self.conversion_settings = ConversionSettings
        self.nsx_backups = None
        self.command_line = CommandLineParsing()
        self.config_data = ConfigData('config.ini', 'gfm', allow_no_value=True)
        self.evaluate_command_line_arguments()
        if self.conversion_settings.conversion_input == 'html':
            self.convert_html()
        else:
            self.convert_nsx()

        self.output_results_if_not_silent_mode()
        self.log_results()
        self.logger.info("Processing Completed - exiting normally")

    def convert_nsx(self):
        self.fetch_nsx_backups()
        self.process_nsx_files()

    @Timer(name="html_conversion", logger=root_logger.info)
    def convert_html(self):
        html_files_to_convert = self.generate_html_file_list()
        self.process_html_files(html_files_to_convert)

    def generate_html_file_list(self):
        if not self.conversion_settings.source.is_file():
            return self.conversion_settings.source.rglob('*.html')   # this is duplicating th nsx code except for rglob do not need rglob on nsx files
        return [self.conversion_settings.source]

    def process_html_files(self, html_files_to_convert):
        html_file_converter = HTMLConverter(self.conversion_settings)
        html_file_count = 0
        for file in html_files_to_convert:
            html_file_converter.convert(file)
            html_file_count += 1

        self._note_page_count = html_file_count

    def fetch_nsx_backups(self):
        nsx_files_to_convert = self.generate_file_list_to_convert()

        self.exit_if_no_nsx_files_found(nsx_files_to_convert)

        self.nsx_backups = [NSXFile(file, self.conversion_settings) for file in nsx_files_to_convert]

    def exit_if_no_nsx_files_found(self, nsx_files_to_convert):
        if not nsx_files_to_convert:
            root_logger.info(f"No .nsx files found at path {self.conversion_settings.source}. Exiting program")
            if not self.conversion_settings.silent:
                print(f'No .nsx files found at {self.conversion_settings.source}')
            sys.exit(1)

    @Timer(name="nsx_conversion", logger=root_logger.info)
    def process_nsx_files(self):
        for nsx_file in self.nsx_backups:
            nsx_file.process_nsx_file()
            self.update_processing_stats(nsx_file)

    def update_processing_stats(self, nsx_file):
        self._note_page_count += nsx_file.note_page_count
        self._note_book_count += nsx_file.note_book_count
        self._image_count += nsx_file.image_count
        self._attachment_count += nsx_file.attachment_count

    def generate_file_list_to_convert(self):
        if not self.conversion_settings.source.is_file():
            return self.conversion_settings.source.glob('*.nsx')
        return [self.conversion_settings.source]

    def evaluate_command_line_arguments(self):

        if self.command_line.args['gui']:
            self.run_gui()
            return

        if self.command_line.args['ini']:
            self.configure_for_ini_settings()
            return

        if self.command_line.args['manual']:
            self.configure_for_manual_settings()
            return

        if not (self.command_line.args['quickset'] is None):
            self.configure_for_quick_setting()
            return

        if self.command_line.args['silent']:
            root_logger.warning(f"Command line option -s  --silent used without -m, -g, q, or -i.  "
                                f"Unable to use Interactive command line due to silence request.  "
                                f"Exiting program")
            sys.exit(0)

        root_logger.info("Starting interactive command line tool")
        self.run_interactive_command_line_interface()

    def add_file_paths_from_command_line_to_settings(self):
        self.conversion_settings.source = self.command_line.args['source']
        self.conversion_settings.export_folder_name = self.command_line.args['export_folder']
        self.conversion_settings.attachment_folder_name = self.command_line.args['attachments']

    def run_interactive_command_line_interface(self):
        command_line_interface = StartUpCommandLineInterface(self.command_line.conversion_setting)
        self.conversion_settings = command_line_interface.run_cli()
        self.conversion_settings.source = self.command_line.args['source']
        self.config_data.conversion_settings = self.conversion_settings  # this will save the setting in the ini file
        self.logger.info("Using conversion settings from interactive command line tool")

    def run_gui(self):
        root_logger.info("Using gui if it was coded....")
        if not self.command_line.args['silent']:
            print("gui")  # run gui

    def configure_for_ini_settings(self):
        # every time I look at his I wonder if values somebody enters after -i on the command line should be used...
        # No they should not.  they have chosen to use ini file and all the settings they need should be in it as
        # they have chosen to use the ini file so ignore any  other options they enter
        root_logger.info("Using settings from config  ini file")
        self.conversion_settings = self.config_data.conversion_settings

    def configure_for_manual_settings(self):
        self.conversion_settings = self.command_line.conversion_setting
        self.config_data.conversion_settings = self.conversion_settings

    def configure_for_quick_setting(self):
        # for a quick setting the source, export folder and attachment folder provided on the command
        # line will be used or the defaults if they were not provided as arguments
        root_logger.info(f"Using quick settings for {self.command_line.args['quickset']}")
        self.conversion_settings = quick_settings.please.provide(self.command_line.args['quickset'])
        self.add_file_paths_from_command_line_to_settings()
        self.config_data.conversion_settings = self.conversion_settings

    def output_results_if_not_silent_mode(self):
        if not self.conversion_settings.silent:
            print("Hello. I'm done")
            self.print_result_if_any(self._note_book_count, 'Note book')
            self.print_result_if_any(self._note_page_count, 'Note page')
            self.print_result_if_any(self._image_count, 'Image')
            self.print_result_if_any(self._attachment_count, 'Attachment')

    @staticmethod
    def print_result_if_any(conversion_count, message):
        if conversion_count == 0:
            return
        plural = ''
        if conversion_count > 1:
            plural = 's'
        print(f'{conversion_count} {message}{plural}')

    def log_results(self):
        self.logger.info(f"{self._note_book_count} Note books")
        self.logger.info(f"{self._note_page_count} Note Pages")
        self.logger.info(f"{self._image_count} Images")
        self.logger.info(f"{self._attachment_count} Attachments")


if __name__ == '__main__':
    notes_converter = NotesConvertor()
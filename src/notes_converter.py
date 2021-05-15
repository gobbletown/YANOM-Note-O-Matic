import logging
import sys
from timer import Timer

from alive_progress import alive_bar

from config_data import ConfigData
import config
from interactive_cli import StartUpCommandLineInterface
from nsx_file_converter import NSXFile
from pandoc_converter import PandocConverter
from file_converter_HTML_to_MD import HTMLToMDConverter
from file_converter_MD_to_HTML import MDToHTMLConverter
from file_converter_MD_to_MD import MDToMDConverter


def what_module_is_this():
    return __name__


class NotesConvertor:
    """
    A class to direct the conversion of note files into alternative output formats.

    Uses the passed in command line arguments to direct flow to use the ini file conversion settings or the
    interactive command line interface to set the conversion settings.  Then using the conversion settings
    directs the conversion of the required source file type. Once conversion is completed a summary of the process
    is displayed.

    """

    def __init__(self, args):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self.logger.debug(f"command line ars are - {args}")
        self.logger.info(f'Program startup')
        self.command_line_args = args
        self.config_data = ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
        self.conversion_settings = None
        self.evaluate_command_line_arguments()
        self._note_page_count = 0
        self._note_book_count = 0
        self._image_count = 0
        self._attachment_count = 0
        self.nsx_backups = None
        self.pandoc_converter = None
        if self.conversion_settings.conversion_input == 'html':
            self.convert_html()
        elif self.conversion_settings.conversion_input == 'markdown':
            self.convert_markdown()
        else:
            self.convert_nsx()

        self.output_results_if_not_silent_mode()
        self.log_results()
        self.logger.info("Processing Completed - exiting normally")

    def convert_markdown(self):
        with Timer(name="md_conversion", logger=self.logger.info, silent=bool(config.silent)):
            file_extension = 'md'
            md_files_to_convert = self.generate_file_list(file_extension)
            self.exit_if_no_files_found(md_files_to_convert, file_extension)

            if self.conversion_settings.export_format == 'html':
                md_file_converter = MDToHTMLConverter(self.conversion_settings, md_files_to_convert)
            else:
                md_file_converter = MDToMDConverter(self.conversion_settings, md_files_to_convert)

            self.process_files(md_files_to_convert, md_file_converter)

    def generate_file_list(self, file_extension):
        if not self.conversion_settings.source.is_file():
            file_list_generator = self.conversion_settings.source_absolute_path.rglob(f'*.{file_extension}')
            file_list = [item for item in file_list_generator]
            return file_list

        return [self.conversion_settings.source]

    def exit_if_no_files_found(self, files_to_convert, file_extension):
        if not files_to_convert:
            self.logger.info(f"No .{file_extension} files found at path {self.conversion_settings.source}. Exiting program")
            if not config.silent:
                print(f'No .{file_extension} files found at {self.conversion_settings.source}')
            sys.exit(0)

    def process_files(self, files_to_convert, file_converter):
        file_count = 0

        print(f"Processing note pages")
        with alive_bar(len(files_to_convert), bar='blocks') as bar:
            for file in files_to_convert:
                file_converter.convert(file)
                file_count += 1
                bar()

        self._note_page_count = file_count

    def convert_html(self):
        with Timer(name="html_conversion", logger=self.logger.info, silent=bool(config.silent)):
            file_extension = 'html'
            html_files_to_convert = self.generate_file_list(file_extension)
            self.exit_if_no_files_found(html_files_to_convert, file_extension)
            html_file_converter = HTMLToMDConverter(self.conversion_settings, html_files_to_convert)
            self.process_files(html_files_to_convert, html_file_converter)

    def convert_nsx(self):
        self.fetch_nsx_backups()
        self.process_nsx_files()

    def fetch_nsx_backups(self):
        file_extension = 'nsx'
        nsx_files_to_convert = self.generate_file_list(file_extension)

        self.exit_if_no_files_found(nsx_files_to_convert, file_extension)

        self.pandoc_converter = PandocConverter(self.conversion_settings)
        self.nsx_backups = [NSXFile(file, self.conversion_settings, self.pandoc_converter) for file in nsx_files_to_convert]

    def process_nsx_files(self):
        with Timer(name="nsx_conversion", logger=self.logger.info, silent=bool(config.silent)):
            for nsx_file in self.nsx_backups:
                nsx_file.process_nsx_file()
                self.update_processing_stats(nsx_file)

    def update_processing_stats(self, nsx_file):
        self._note_page_count += nsx_file.note_page_count
        self._note_book_count += nsx_file.note_book_count
        self._image_count += nsx_file.image_count
        self._attachment_count += nsx_file.attachment_count

    def evaluate_command_line_arguments(self):
        self.configure_for_ini_settings()

        if self.command_line_args['silent'] or self.command_line_args['ini']:
            return

        self.logger.debug("Starting interactive command line tool")
        self.run_interactive_command_line_interface()

    def run_interactive_command_line_interface(self):
        command_line_interface = StartUpCommandLineInterface(self.conversion_settings)
        self.conversion_settings = command_line_interface.run_cli()
        self.conversion_settings.source = self.command_line_args['source']
        self.config_data.conversion_settings = self.conversion_settings  # this will save the setting in the ini file
        self.logger.info("Using conversion settings from interactive command line tool")

    def configure_for_ini_settings(self):
        self.logger.info("Using settings from config  ini file")
        self.conversion_settings = self.config_data.conversion_settings

    def output_results_if_not_silent_mode(self):
        if not config.silent:
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
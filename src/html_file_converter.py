from pandoc_converter import PandocConverter
import logging
from globals import APP_NAME
import inspect
from pathlib import Path
from post_processing import ObsidianImageTagFormatter
from checklist_processing import HTMLInputMDOutputChecklistProcessor


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class HTMLConverter:
    def __init__(self, conversion_settings):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._html_file = Path
        self._html_file_content = ''
        self._pre_processed_content = ''
        self._post_processed_content = ''
        self._converted_content = ''
        self._conversion_settings = conversion_settings
        self._pandoc_converter = PandocConverter(self._conversion_settings)
        self._pre_processor = None
        self._checklist_processor = None
        self._note_page_count = 0

    def convert(self, file):
        self._html_file = Path(file)
        self.read_html_file()
        self.__pre_process_content()
        self.__convert_html_content()
        self.__post_process_content()
        self.write_converted_content()

    def read_html_file(self):
        self._html_file_content = self._html_file.read_text()

    def __convert_html_content(self):
        self.logger.info(f"Converting content of '{self._html_file}'")
        self._converted_content = self._pandoc_converter.convert_using_strings(self._pre_processed_content, str(self._html_file))

    def write_converted_content(self):
        output_path = self._html_file.parent / (self._html_file.stem + '.md')
        output_path.write_text(self._post_processed_content, encoding="utf-8")

    def __pre_process_content(self):
        self._checklist_processor = HTMLInputMDOutputChecklistProcessor(self._html_file_content)
        self._pre_processed_content = self._checklist_processor.processed_html
        # self._pre_processed_content = self._html_file_content

    def __post_process_content(self):
        self._post_processed_content = self._converted_content
        self.__format_images_links()
        self.__add_check_lists()
        self.__add_one_last_line_break()

    def __format_images_links(self):
        if self._conversion_settings.export_format == 'obsidian':
            obsidian_image_link_formatter = ObsidianImageTagFormatter(self._post_processed_content)
            self._post_processed_content = obsidian_image_link_formatter.post_processed_content

    def __add_check_lists(self):
        self._post_processed_content = self._checklist_processor.add_checklist_items_to(self._post_processed_content)

    def __add_one_last_line_break(self):
        self._post_processed_content = f'{self._post_processed_content}\n'
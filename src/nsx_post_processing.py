from abc import ABC, abstractmethod
import logging
from globals import APP_NAME
import inspect

from image_processing import ObsidianImageTagFormatter


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class PostProcessing(ABC):
    """Abstract class representing a pre conversion note formatting """

    @abstractmethod
    def post_process_note_page(self):
        pass


class NoteStationPostProcessing(PostProcessing):
    def __init__(self, note):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._note = note
        self._conversion_settings = note.conversion_settings
        self._yaml_header = ''
        self._post_processed_content = note.converted_content
        self._pre_processor = note.pre_processor
        self.post_process_note_page()

    def post_process_note_page(self):
        if self._conversion_settings.front_matter_format != 'none':
            self.__add_meta_data()
        self.__add_check_lists()
        self.__format_images_links()
        self.__add_one_last_line_break()

    def __add_meta_data(self):
        if self._note.conversion_settings.front_matter_format != 'none':
            self._post_processed_content = self._pre_processor.header_generator.add_metadata_md_to_content(self._post_processed_content)

    def __add_check_lists(self):
        self._post_processed_content = self._note.pre_processor.checklist_processor.add_checklist_items_to(self._post_processed_content)

    def __format_images_links(self):
        if self._conversion_settings.export_format == 'obsidian':
            obsidian_image_link_formatter = ObsidianImageTagFormatter(self._post_processed_content, 'obsidian')
            self._post_processed_content = obsidian_image_link_formatter.processed_content

    def __add_one_last_line_break(self):
        self._post_processed_content = f'{self._post_processed_content}\n'

    @property
    def post_processed_content(self):
        return self._post_processed_content

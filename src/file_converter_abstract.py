from abc import ABC, abstractmethod
import logging
from pathlib import Path
import re

from bs4 import BeautifulSoup

import config
import file_writer
from image_processing import ObsidianImageTagFormatter
from pandoc_converter import PandocConverter


def what_module_is_this():
    return __name__


class FileConverter(ABC):
    def __init__(self, conversion_settings, files_to_convert):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._file = None
        self._files_to_convert = files_to_convert
        self._file_content = ''
        self._meta_content = {}
        self._pre_processed_content = ''
        self._post_processed_content = ''
        self._converted_content = ''
        self._conversion_settings = conversion_settings
        self._out_put_extension = self.set_out_put_file_extension()
        self._pandoc_converter = PandocConverter(self._conversion_settings)
        self._pre_processor = None
        self._checklist_processor = None
        self._image_processor = None
        self._metadata_processor = None
        self._note_page_count = 0

    @abstractmethod
    def pre_process_content(self):  # pragma: no cover
        pass

    @abstractmethod
    def post_process_content(self):  # pragma: no cover
        pass

    @abstractmethod
    def parse_metadata_if_required(self):  # pragma: no cover
        pass

    @abstractmethod
    def add_meta_data_if_required(self):  # pragma: no cover
        pass

    def update_note_links(self, content, source_extension='', target_extension=''):
        # create a basic file name filter to rename only those files that are being modified
        # only compares file names not full paths.. so limited but will be enough for many cases
        links_that_can_be_renamed = [Path(file).stem for file in self._files_to_convert]

        soup = BeautifulSoup(content, 'html.parser')
        for a in soup.findAll(href=True):
            link = re.search(fr'^((?!https).*).{source_extension}$', a['href'])  # extract the actual link
            if link is not None:
                if Path(str(link.group(1))).name in links_that_can_be_renamed:  # only names in list being processed
                    a['href'] = str(link.group(1)) + '.' + target_extension

        return str(soup)

    def set_out_put_file_extension(self):
        if self._conversion_settings.export_format == 'html':
            return '.html'
        return '.md'

    def convert(self, file):
        self._file = Path(file)
        self.read_file()
        self.pre_process_content()
        self.convert_content()
        self.post_process_content()
        self.write_post_processed_content()

    def read_file(self):
        self._file_content = self._file.read_text(encoding='utf-8')

    def convert_content(self):
        self.logger.info(f"Converting content of '{self._file}'")
        self._converted_content = self._pandoc_converter.convert_using_strings(self._pre_processed_content,
                                                                               str(self._file))

    def pre_process_obsidian_image_links_if_required(self):
        if self._conversion_settings.markdown_conversion_input == 'obsidian':
            self.logger.debug(f"Pre process obsidian image links")
            obsidian_image_link_formatter = ObsidianImageTagFormatter(self._pre_processed_content, 'gfm')
            self._pre_processed_content = obsidian_image_link_formatter.processed_content

    def post_process_obsidian_image_links_if_required(self):
        if self._conversion_settings.export_format == 'obsidian':
            self.logger.debug(f"Post process obsidian image links")
            obsidian_image_link_formatter = ObsidianImageTagFormatter(self._post_processed_content, 'obsidian')
            self._post_processed_content = obsidian_image_link_formatter.processed_content

    def write_post_processed_content(self):
        self.logger.info(f"Writing new file {self._file.stem + self._out_put_extension}")
        absolute_path = self._file.parent / (self._file.stem + self._out_put_extension)
        # absolute_path.write_text(self._post_processed_content, encoding="utf-8")
        file_writer.write_text(absolute_path, self._post_processed_content)

    def rename_target_file_if_already_exists(self):
        n = 0
        target_path = Path(self._file.parent, f'{self._file.stem}{self._out_put_extension}')

        if not target_path.exists():  # no need for renaming
            return

        check_target_path = target_path
        while check_target_path.exists():
            n += 1
            check_target_path = Path(self._file.parent, f'{self._file.stem}-old-{n}{self._out_put_extension}')

        target_path.replace(check_target_path)

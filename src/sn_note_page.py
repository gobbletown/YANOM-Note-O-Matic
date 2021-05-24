import logging
import time
from pathlib import Path

import config
import file_writer
import helper_functions
from nsx_post_processing import NoteStationPostProcessing
from nsx_pre_processing import NoteStationPreProcessing
import sn_attachment


def what_module_is_this():
    return __name__


class NotePage:
    def __init__(self, nsx_file, note_id, note_json):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._nsx_file = nsx_file
        self._pandoc_converter = nsx_file.pandoc_converter
        self._conversion_settings = nsx_file.conversion_settings
        self._note_id = note_id
        self._note_json = note_json
        self._title = self._note_json['title']
        self._original_title = self._note_json['title']
        self._format_ctime_and_mtime_if_required()
        self._raw_content = self._note_json['content']
        self._parent_notebook = self._note_json['parent_id']
        self._attachments_json = self._note_json['attachment']
        self._attachments = {}
        self._pre_processed_content = ''
        self._converted_content = ''
        self._notebook_folder_name = ''
        self._file_name = ''
        self._full_path = ''
        self._image_count = 0
        self._attachment_count = 0
        self._pre_processor = None
        self._post_processor = None

    def _format_ctime_and_mtime_if_required(self):
        if self._conversion_settings.front_matter_format != 'none' \
                or self._conversion_settings.creation_time_in_exported_file_name is True:
            self._note_json['ctime'] = time.strftime('%Y%m%d%H%M', time.localtime(self._note_json['ctime']))
            self._note_json['mtime'] = time.strftime('%Y%m%d%H%M', time.localtime(self._note_json['mtime']))
            pass

    def process_note(self):
        self.logger.info(f"Processing note page '{self._title}' - {self._note_id}")
        self.create_attachments()
        self.process_attachments()
        self.pre_process_content()
        self.convert_data()
        if not self.conversion_settings.export_format == 'html':
            self.post_process_content()
        self.store_file()
        self.logger.debug(f"Processing of note page '{self._title}' - {self._note_id}  completed.")

    def _create_file_name(self):
        dirty_filename = self._append_file_extension()
        self._file_name = helper_functions.generate_clean_path(dirty_filename)

    def _append_file_extension(self):
        if self._conversion_settings.export_format == 'html':
            return f"{self._title}.html"

        return f"{self._title}.md"

    def _generate_absolute_path(self):
        path_to_file = Path(self._conversion_settings.working_directory, config.DATA_DIR,
                            self._conversion_settings.export_folder_name, self._notebook_folder_name, self._file_name)

        absolute_file_path = helper_functions.find_valid_full_file_path(path_to_file)

        return absolute_file_path

    def generate_filenames_and_paths(self):
        self._create_file_name()
        self._full_path = self._generate_absolute_path()
        self._file_name = self._full_path.name

    @property
    def parent_notebook(self):
        return self._parent_notebook

    def create_attachments(self):
        for attachment_id in self._attachments_json:
            if self._attachments_json[attachment_id]['type'].startswith('image'):
                self._attachments[attachment_id] = sn_attachment.ImageNSAttachment(self, attachment_id)
                self._image_count += 1
            else:
                self._attachments[attachment_id] = sn_attachment.FileNSAttachment(self, attachment_id)
                self._attachment_count += 1

        return self._image_count, self._attachment_count

    def process_attachments(self):
        self.logger.debug('Process attachments')
        for attachment_id in self._attachments:
            self._attachments[attachment_id].process_attachment()

    def pre_process_content(self):
        self._pre_processor = NoteStationPreProcessing(self)
        self._pre_processed_content = self._pre_processor.pre_processed_content

    def convert_data(self):
        if self.conversion_settings.export_format == 'html':
            self._converted_content = self._pre_processed_content
            return

        self.logger.debug(f"Converting content of '{self._title}' - {self._note_id}")
        self._converted_content = self._pandoc_converter.convert_using_strings(self._pre_processed_content, self._title)

    def post_process_content(self):
        self._post_processor = NoteStationPostProcessing(self)
        self._converted_content = self._post_processor.post_processed_content

    def increment_duplicated_title(self, list_of_existing_titles):
        """
        Add incrementing number to title for duplicates notes in a notebook.

        When a note title is found to already exist in a notebook add a number to the end of the title, incrementing
        if required when there are multiple duplicates
        """
        this_title = self._title
        n = 0

        while this_title in list_of_existing_titles:
            n += 1
            this_title = f'{self._title}-{n}'

        self._title = this_title

    def store_file(self):
        file_writer.store_file(self._full_path, self._converted_content)

    @property
    def title(self):
        return self._title

    @property
    def original_title(self):
        return self._original_title

    @property
    def note_id(self):
        return self._note_id

    @property
    def notebook_folder_name(self):
        return self._notebook_folder_name

    @notebook_folder_name.setter
    def notebook_folder_name(self, title):
        self._notebook_folder_name = helper_functions.generate_clean_path(title)

    @property
    def file_name(self):
        return self._file_name

    @property
    def full_path(self):
        return self._full_path

    @property
    def converted_content(self):
        return self._converted_content

    @property
    def note_json(self):
        return self._note_json

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @property
    def nsx_file(self):
        return self._nsx_file

    @property
    def raw_content(self):
        return self._raw_content

    @property
    def attachments(self):
        return self._attachments

    @property
    def image_count(self):
        return self._image_count

    @image_count.setter
    def image_count(self, value):
        self._image_count = value

    @property
    def attachment_count(self):
        return self._attachment_count

    @attachment_count.setter
    def attachment_count(self, value):
        self._attachment_count = value

    @property
    def conversion_settings(self):
        return self._conversion_settings

    @property
    def parent_notebook(self):
        return self._parent_notebook

    @parent_notebook.setter
    def parent_notebook(self, value):
        self._parent_notebook = value

    @property
    def pre_processor(self):
        return self._pre_processor

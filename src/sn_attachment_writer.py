import inspect
import logging
from pathlib import Path

from globals import APP_NAME, DATA_DIR
from helper_functions import generate_new_filename, find_working_directory
import sn_attachment


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class AttachmentWriter:
    def __init__(self, nsx_file):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f'{__name__} - Creating an instance of {what_class_is_this(self)}')
        self.nsx_file = nsx_file
        self._current_directory_path = None
        self._output_folder = nsx_file.conversion_settings.export_folder_name
        self._attachment_folder = nsx_file.conversion_settings.attachment_folder_name
        self._notebook_folder = None
        self._output_file_name = None
        self._input_file_name = None
        self._path_relative_to_notebook = None
        self._output_file_path = None
        self._relative_path = None
        self.find_current_directory_path()

    def find_current_directory_path(self):
        self._current_directory_path, message = find_working_directory()
        self.logger.info(message)

    def store_nsx_attachment(self, attachment):
        self.generate_relative_path(attachment)
        self.generate_output_path(attachment)

        self.logger.info(f"Storing attachment {attachment.file_name} as {self._output_file_name}")
        Path(self._output_file_path).write_bytes(self.nsx_file.fetch_attachment_file(attachment.filename_inside_nsx))

    def store_chart_attachment(self, attachment):
        self.generate_relative_path(attachment)
        self.generate_output_path(attachment)

        self.logger.info(f"Storing attachment {attachment.file_name} as {self._output_file_name}")
        if isinstance(attachment, sn_attachment.ChartStringNSAttachment):
            Path(self._output_file_path).write_text(attachment.chart_file_like_object)
            return

        Path(self._output_file_path).write_bytes(attachment.chart_file_like_object.getbuffer())

    def generate_relative_path(self, attachment):
        self._path_relative_to_notebook = Path(self._attachment_folder, attachment.file_name)

    def generate_output_path(self, attachment):
        path = Path(self._current_directory_path, DATA_DIR, self._output_folder,
                    attachment.notebook_folder_name,
                    self._path_relative_to_notebook)

        while path.is_file():
            path = generate_new_filename(path)

        self._output_file_name = path.name
        self._output_file_path = path
        self._relative_path = (Path(self._attachment_folder, self._output_file_name))

    @property
    def output_file_name(self):
        return self._output_file_name

    @property
    def output_file_path(self):
        return self._output_file_path

    @property
    def relative_path(self):
        return self._relative_path

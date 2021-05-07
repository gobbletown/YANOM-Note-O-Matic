"""
Provide classes for provision of conversion settings for manual or specific pre configured sets of conversion settings

"""
from abc import abstractmethod
import os
import inspect
import logging
from pathlib import Path
import sys

from custom_inherit import DocInheritMeta

from globals import APP_NAME, DATA_DIR
from helper_functions import generate_clean_path, find_working_directory
import object_factory


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class ConversionSettingsError(Exception):
    pass


class ConversionSettingProvider(object_factory.ObjectFactory):
    """
    ConversionSettingProvider generator

    Used to generate configuration settings for specific 'quick settings' or a manual setting where the user selects
    all options, manual is also used by the ConfigData class to pass settings from a config.ini file

    Yields
    ------
    Child of ConversionSettings
        Requested child object is generated based on request string value.

    """

    def provide(self, conversion_setting_type, **_ignored):
        return self.create(conversion_setting_type)


class ConversionSettings(metaclass=DocInheritMeta(style="numpy", abstract_base_class=True)):
    """
    Conversion settings required to convert input formats to export formats.

    Child classes implement specific 'quick settings' for pre-known typical formats for files or notes programs,
    or a user configured conversion setting where a quick setting does not meet a required need.

    Attributes
    ----------
    validation_values : dict
        a static dictionary that is used by ConfigData class to validate ini files read from disk.
    logger : logger object
        used for program logging
    _valid_conversion_inputs : list of strings
        List of file formats that can be converted
    _valid_markdown_conversion_inputs : list of strings
        List of markdown formats that can be converted
    _valid_quick_settings : list of strings
        Quick settings strings that are used to create 'default' conversions for various program and file types.
        Also are the values used in an object generator to create child classes
    _valid_export_formats : list of strings
        Export format names used to trigger specific conversion behaviour in style of file type
    _silent : bool
        Run program with no output to command line
    _source : pathlib.Path
        Directory to search for nsx files or path to specific nsx file
    _conversion_input : str
        The type of file to be converted
    _markdown_conversion_input : str
        The markdown format for the markdown files if they are the file type to be converted
    _quick_setting: str
        A trigger string used for a default set for some of the following filed values
    _export_format: str
        The export format to be used
    _include_meta_data: bool
        Add available meta data, not in a note body, to the main text of the exported note
    _metadata_front_matter_format: str
        Meta data to be placed in a yaml/json/toml front matter section above the body of the main text
    _insert_title: bool
        Include title in the included meta data
    _insert_creation_time: bool
        Include the note creation time in the included meta data
    _insert_modified_time: bool
        Include the note modified time iin the included meta data
    _include_tags: bool
        Include tags in the meta data
    _tag_prefix: str
        Prefix to place on tags
    _spaces_in_tags: bool
        Allow spaces in tag names
    _split_tags: bool
        Split tags into separate tags where the input was a grouped tag format e.g. /coding/python -> coding python
    _export_folder_name: pathlib.Path
        Path object for the sub-directory name to place exported notes into
    _attachment_folder_name: pathlib.Path
        Path object for the sub-directory name within the export folder to place images and attachments
    _creation_time_in_exported_file_name: bool
        Include the note creation time on the end of the file name

    Methods
    -------
    set_settings()
        Change attribute values to achieve a specific conversion process

    """
    # These values are used here and in config_data
    validation_values = {
        'execution_mode': {
            'silent': ('True', 'False')
        },
        'conversion_inputs': {
            'conversion_input': ('nsx', 'html', 'markdown')
        },
        'markdown_conversion_inputs': {
            'markdown_conversion_input': ('obsidian', 'gfm', 'commonmark', 'q_own_notes', 'pandoc_markdown_strict', 'pandoc_markdown', 'multimarkdown')
        },
        'quick_settings': {
            'quick_setting': ('manual', 'q_own_notes', 'obsidian', 'gfm', 'commonmark', 'pandoc_markdown', 'pandoc_markdown_strict', 'multimarkdown', 'html')
        },
        'export_formats': {
            'export_format': ('q_own_notes', 'obsidian', 'gfm', 'pandoc_markdown', 'commonmark', 'pandoc_markdown_strict', 'multimarkdown', 'html')
        },
        'meta_data_options': {
            'metadata_front_matter_format': ('yaml', 'toml', 'json', 'text', 'none'),
            'metadata_schema': '',
            'tag_prefix': '',
            'spaces_in_tags': ('True', 'False'),
            'split_tags': ('True', 'False')
        },
        'table_options': {
            'first_row_as_header': ('True', 'False'),
            'first_column_as_header': ('True', 'False')
        },
        'file_options': {
            'source': '',
            'export_folder_name': '',
            'attachment_folder_name': '',
            'creation_time_in_exported_file_name': ('True', 'False')
        }
    }

    def __init__(self):
        # if you change any of the following values changes are likely to affect the quick settings child classes
        # and the ConfigFileValidationSettings class
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._valid_conversion_inputs = list(self.validation_values['conversion_inputs']['conversion_input'])
        self._valid_markdown_conversion_inputs = list(self.validation_values['markdown_conversion_inputs']['markdown_conversion_input'])
        self._valid_quick_settings = list(self.validation_values['quick_settings']['quick_setting'])
        self._valid_export_formats = list(self.validation_values['export_formats']['export_format'])
        self._valid_front_matter_formats = list(self.validation_values['meta_data_options']['metadata_front_matter_format'])
        self._silent = False
        self._source = '' # os.getcwd() + '/' + DATA_DIR
        self._conversion_input = 'nsx'
        self._markdown_conversion_input = 'gfm'
        self._quick_setting = 'gfm'
        self._export_format = 'gfm'
        self._front_matter_format = 'yaml'
        self._metadata_schema = []
        self._tag_prefix = '#'
        self._spaces_in_tags = False
        self._split_tags = False
        self._first_row_as_header = True
        self._first_column_as_header = True
        self._export_folder_name = 'notes'
        self._attachment_folder_name = 'attachments'
        self._creation_time_in_exported_file_name = False
        self.set_settings()

    def __str__(self):
        return f"{self.__class__.__name__}(valid_conversion_inputs={self.valid_conversion_inputs}, " \
               f"valid_markdown_conversion_inputs='{self.valid_markdown_conversion_inputs}', " \
               f"valid_quick_settings='{self.valid_quick_settings}', " \
               f"valid_export_formats='{self.valid_export_formats}', " \
               f"valid_front_matter_formats]'{self.valid_front_matter_formats}', " \
               f"silent={self.silent}, conversion_input={self._conversion_input}, " \
               f"markdown_conversion_input='{self._markdown_conversion_input}, quick_setting='{self.quick_setting}', " \
               f"export_format='{self.export_format}', " \
               f"yaml_front_matter={self.front_matter_format}, metadata_schema='{self.metadata_schema}', " \
               f"tag_prefix='{self.tag_prefix}', " \
               f"first_row_as_header={self._first_row_as_header}, " \
               f"first_column_as_header={self._first_column_as_header}" \
               f"spaces_in_tags={self.spaces_in_tags}, split_tags={self.split_tags}, " \
               f"export_folder_name='{self.export_folder_name}', " \
               f"attachment_folder_name='{self.attachment_folder_name}', " \
               f"creation_time_in_exported_file_name='{self.creation_time_in_exported_file_name})'"

    def __repr__(self):
        return f"{self.__class__.__name__}(valid_conversion_inputs={self.valid_conversion_inputs}, " \
               f"valid_markdown_conversion_inputs='{self.valid_markdown_conversion_inputs}', " \
               f"valid_quick_settings='{self.valid_quick_settings}', " \
               f"valid_export_formats='{self.valid_export_formats}', " \
               f"valid_front_matter_formats]'{self.valid_front_matter_formats}', " \
               f"silent={self.silent}, conversion_input={self._conversion_input}, " \
               f"markdown_conversion_input='{self._markdown_conversion_input}, quick_setting='{self.quick_setting}', " \
               f"export_format='{self.export_format}', " \
               f"yaml_front_matter={self.front_matter_format}, metadata_schema='{self.metadata_schema}', " \
               f"tag_prefix='{self.tag_prefix}', " \
               f"first_row_as_header={self._first_row_as_header}, " \
               f"first_column_as_header={self._first_column_as_header}" \
               f"spaces_in_tags={self.spaces_in_tags}, split_tags={self.split_tags}, " \
               f"export_folder_name='{self.export_folder_name}', " \
               f"attachment_folder_name='{self.attachment_folder_name}', " \
               f"creation_time_in_exported_file_name='{self.creation_time_in_exported_file_name})'"

    @abstractmethod
    def set_settings(self):
        pass

    @property
    def valid_conversion_inputs(self):
        return self._valid_conversion_inputs

    @property
    def valid_markdown_conversion_inputs(self):
        return self._valid_markdown_conversion_inputs

    @property
    def valid_quick_settings(self):
        return self._valid_quick_settings

    @property
    def valid_export_formats(self):
        return self._valid_export_formats

    @property
    def valid_front_matter_formats(self):
        return self._valid_front_matter_formats

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self, value: bool):
        self._silent = value

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if value == '':
            self._source, message = find_working_directory()
            self._source = Path(self._source, DATA_DIR)
            self.logger.error(f"Using {self._source} as source directory")
        elif Path(value).exists():
            self._source = Path(value)
        else:
            self.logger.error(f"Invalid source location - {value} - Check command line argument OR config.ini entry - Exiting program")
            if not self.silent:
                sys.exit(f"Invalid source location - {value} - Check command line argument OR config.ini entry. Exiting program")


    @property
    def conversion_input(self):
        return self._conversion_input

    @conversion_input.setter
    def conversion_input(self, value):
        self._conversion_input = value

    @property
    def markdown_conversion_input(self):
        return self._markdown_conversion_input

    @markdown_conversion_input.setter
    def markdown_conversion_input(self, value):
        self._markdown_conversion_input = value

    @property
    def quick_setting(self):
        return self._quick_setting

    @quick_setting.setter
    def quick_setting(self, value):
        if value is None:
            return
        if value in self.valid_quick_settings:
            self._quick_setting = value
            return
        else:
            raise ValueError(f"Invalid value for quick setting. "
                             f"Attempted to use {value}, valid values are {self.valid_quick_settings}")

    @property
    def export_format(self):
        return self._export_format

    @export_format.setter
    def export_format(self, value):
        if value in self.valid_export_formats:
            self._export_format = value
        else:
            raise ValueError(f"Invalid value for export format. "
                             f"Attempted to use {value}, valid values are {self.valid_export_formats}")

    @property
    def metadata_schema(self):
        return self._metadata_schema

    @metadata_schema.setter
    def metadata_schema(self, value):
        if isinstance(value, str):
            values = value.split(",")
            self._metadata_schema = [value.strip() for value in values]
            return
        if isinstance(value, list):
            self._metadata_schema = value
            return
        self.logger.warning(f'Invalid creation time key provided {value}')

    @property
    def front_matter_format(self):
        return self._front_matter_format

    @front_matter_format.setter
    def front_matter_format(self, value: str):
        self._front_matter_format = value

    @property
    def tag_prefix(self):
        return self._tag_prefix

    @tag_prefix.setter
    def tag_prefix(self, value: str):
        self._tag_prefix = value

    @property
    def spaces_in_tags(self):
        return self._spaces_in_tags

    @spaces_in_tags.setter
    def spaces_in_tags(self, value: bool):
        self._spaces_in_tags = value

    @property
    def split_tags(self):
        return self._split_tags

    @split_tags.setter
    def split_tags(self, value: bool):
        self._split_tags = value

    @property
    def first_row_as_header(self):
        return self._first_row_as_header

    @first_row_as_header.setter
    def first_row_as_header(self, value: bool):
        self._first_row_as_header = value

    @property
    def first_column_as_header(self):
        return self._first_column_as_header

    @first_column_as_header.setter
    def first_column_as_header(self, value: bool):
        self._first_column_as_header = value

    @property
    def export_folder_name(self):
        return self._export_folder_name

    @export_folder_name.setter
    def export_folder_name(self, value):
        self._export_folder_name = generate_clean_path(value)

    @property
    def attachment_folder_name(self):
        return self._attachment_folder_name

    @attachment_folder_name.setter
    def attachment_folder_name(self, value):
        self._attachment_folder_name = generate_clean_path(value)

    @property
    def creation_time_in_exported_file_name(self):
        return self._creation_time_in_exported_file_name

    @creation_time_in_exported_file_name.setter
    def creation_time_in_exported_file_name(self, value: bool):
        self._creation_time_in_exported_file_name = value

    @property
    def creation_time_key(self):
        return self._creation_time_key

    @creation_time_key.setter
    def creation_time_key(self, value):
        if isinstance(value, str):
            self._creation_time_key = value
            return
        self.logger.warning(f'Invalid creation time key provided {value}')


class ManualConversionSettings(ConversionSettings):
    """
    Manual conversion settings to convert input formats to export formats.

    Used for user configured selections and ConfigData Class to provide conversions read from ini files.
    """

    def set_settings(self):
        """Set initial conversion settings for a manual conversion setting"""
        self.logger.info("Manual conversion settings")
        self.quick_setting = 'manual'
        self.front_matter_format = 'none'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']
        self.spaces_in_tags = False
        self.split_tags = False
        self.first_row_as_header = False
        self.first_column_as_header = False


class QOwnNotesConversionSettings(ConversionSettings):
    """
    QOwnNotes conversion settings to convert input formats to format suitable for QOwnNotes users.
    """

    def set_settings(self):
        self.logger.info("QOwnNotes Setting conversion settings")
        self.quick_setting = 'q_own_notes'
        self.export_format = 'q_own_notes'
        self.front_matter_format = 'yaml'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class GfmConversionSettings(ConversionSettings):
    """
    Git-flavoured markdown conversion settings to convert input formats to gfm format.
    """

    def set_settings(self):
        self.logger.info("GFM conversion settings")
        self.quick_setting = 'gfm'
        self.front_matter_format = 'yaml'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class ObsidianConversionSettings(ConversionSettings):
    """
    Obsidian conversion settings to convert input formats to format suitable for Obsidian users.
    """

    def set_settings(self):
        self.logger.info("Obsidian conversion settings")
        self.quick_setting = 'obsidian'
        self.export_format = 'obsidian'
        self.front_matter_format = 'yaml'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class CommonmarkConversionSettings(ConversionSettings):
    """
    Commonmark conversion settings
    """

    def set_settings(self):
        self.logger.info("Commonmark conversion settings")
        self.quick_setting = 'commonmark'
        self.export_format = 'commonmark'
        self.front_matter_format = 'yaml'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class PandocMarkdownConversionSettings(ConversionSettings):
    """
    Pandoc Markdown conversion settings.
    """

    def set_settings(self):
        self.logger.info("Pandoc markdown conversion settings")
        self.quick_setting = 'pandoc_markdown'
        self.export_format = 'pandoc_markdown'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class MultiMarkdownConversionSettings(ConversionSettings):
    """
    MultiMarkdown conversion settings.
    """

    def set_settings(self):
        self.logger.info("MultiMarkdown conversion settings")
        self.quick_setting = 'multimarkdown'
        self.export_format = 'multimarkdown'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class PandocMarkdownStrictConversionSettings(ConversionSettings):
    """
     Pandoc Markdown-strict conversion settings.
    """

    def set_settings(self):
        self.logger.info("Pandoc Markdown Strict Setting conversion settings")
        self.quick_setting = 'pandoc_markdown_strict'
        self.export_format = 'pandoc_markdown_strict'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']


class HTMLConversionSettings(ConversionSettings):
    """
    HTML conversion settings to convert input formats to HTML files plus attachments in a folder.
    """

    def set_settings(self):
        self.logger.info("HTML conversion settings")
        self.export_format = 'html'
        self.quick_setting = 'html'
        self.front_matter_format = 'yaml'
        self.metadata_schema = []
        if self.conversion_input == 'nsx':
            self.metadata_schema = ['title', 'ctime', 'mtime', 'tag']



please = ConversionSettingProvider()
please.register_builder('manual', ManualConversionSettings)
please.register_builder('q_own_notes', QOwnNotesConversionSettings)
please.register_builder('gfm', GfmConversionSettings)
please.register_builder('obsidian', ObsidianConversionSettings)
please.register_builder('commonmark', CommonmarkConversionSettings)
please.register_builder('pandoc_markdown', PandocMarkdownConversionSettings)
please.register_builder('pandoc_markdown_strict', PandocMarkdownStrictConversionSettings)
please.register_builder('multimarkdown', MultiMarkdownConversionSettings)
please.register_builder('html', HTMLConversionSettings)

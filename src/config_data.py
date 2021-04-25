from configparser import ConfigParser
import inspect
import logging
from pathlib import Path
import sys

from globals import APP_NAME
from interactive_cli import InvalidConfigFileCommandLineInterface
from conversion_settings import ConversionSettings
import conversion_settings


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class ConfigException(Exception):
    pass


class ConfigData(ConfigParser):
    """
    Read, verify, update and write config.ini files

    Attributes
    ----------
    logger : logging object
        used for program logging
    config_file : str
        name of the configuration file to be parsed and to use for storing config data
    default_quick_setting :  str
        setting to be used if the config.ini is found to be invalid and uses chooses to use the default
    conversion_settings :  Child of ConversionSettings, holds config data in a format to be used outside of the class
    validation_values :  dict
        holds the values required to validate a config file read from disk

    """

    def __init__(self, config_file, default_quick_setting, **kwargs):
        super().__init__(**kwargs)
        # Note: allow_no_value=True  allows for #comments in the ini file
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._config_file = config_file
        self._default_quick_setting = default_quick_setting
        self._conversion_settings = conversion_settings.please.provide('manual')
        self._validation_values = self._conversion_settings.validation_values
        self.__read_config_file()
        self.__validate_config_file()
        self.__generate_conversion_settings_from_parsed_config_file_data()
        self.logger.info(f"Settings from config.ini are {self._conversion_settings}")

    @property
    def conversion_settings(self):
        return self._conversion_settings

    @conversion_settings.setter
    def conversion_settings(self, value):
        """
        Receive a conversion setting as a quick setting string of a ConversionSettings object,
        set the _conversion_setting, generate and save config ini file for the setting received.

        Parameters
        ----------
        value : str or ConversionSettings
            If str must be a valid quick_setting string value.

        """
        if type(value) is str:
            self.__generate_conversion_settings_using_quick_settings_string(value)
            return

        self.__generate_conversion_settings_using_quick_settings_object(value)

    def __generate_conversion_settings_using_quick_settings_string(self, value):
        if value in self._conversion_settings.valid_quick_settings:
            self.load_and_save_config_from_conversion_quick_setting_string(value)
            return

        self.logger.error(f"Passed invalid value - {value} - not a recognised quick setting string")
        raise ValueError(f"Conversion setting parameter must be a valid quick setting string "
                         f"{self._conversion_settings.valid_quick_settings} received '{value}'")

    def __generate_conversion_settings_using_quick_settings_object(self, value):
        if isinstance(value, ConversionSettings):
            self.load_and_save_config_from_conversion_settings_obj(value)
            return

        self.logger.error(f"Passed invalid value - {value}")
        raise TypeError(f"Conversion setting parameter must be a valid quick setting "
                        f"{self._conversion_settings.valid_quick_settings} string or a ConversionSettings object")

    def __validate_config_file(self):
        """
        Validate config data.  Errors in the data prompt user to create a new default configuration or exit the program

        """
        self.logger.debug("attempting to validate config file")
        try:
            self.__validate_config()
            self.logger.info("config file validated")
        except ConfigException as e:
            self.logger.warning(f"Config file invalid \n{e}")

            ask_what_to_do = InvalidConfigFileCommandLineInterface()
            what_to_do = ask_what_to_do.run_cli()
            if what_to_do == 'exit':
                sys.exit(0)
            self.logger.info("User chose to create default file")

            self.load_and_save_config_from_conversion_quick_setting_string(self._default_quick_setting)

    def __validate_config(self):
        """
        Validate the current Config Data for any errors by comparing to a set of validation values.

        Errors will raise a ConfigException

        """
        for section, keys in self._validation_values.items():
            if section not in self:
                raise ConfigException(f'Missing section {section} in the config ini file')

            for key, values in keys.items():
                # if key not in self[section] or self[section][key] == '':
                if key not in self[section]:
                    raise ConfigException(f'Missing erntry for {key} under section {section} in the config ini file')

                if values:
                    if self[section][key] not in values:
                        raise ConfigException(f'Invalid value of "{self[section][key]}" for {key} under section {section} in the config file')

    def __generate_conversion_settings_from_parsed_config_file_data(self):
        """
        Transcribe the values in a ConversionSettings object into the ConfigParser format used by this class

        """
        self._conversion_settings.silent = self['execution_mode']['silent']
        self._conversion_settings.conversion_input = self['conversion_inputs']['conversion_input']
        self._conversion_settings.markdown_conversion_input = \
            self['markdown_conversion_inputs']['markdown_conversion_input']
        self._conversion_settings.quick_setting = self['quick_settings']['quick_setting']
        self._conversion_settings.export_format = self['export_formats']['export_format']
        self._conversion_settings.front_matter_format = self['meta_data_options']['metadata_front_matter_format']
        self._conversion_settings.metadata_schema = self['meta_data_options']['metadata_schema']
        self._conversion_settings.tag_prefix = self['meta_data_options']['tag_prefix']
        self._conversion_settings.spaces_in_tags = self['meta_data_options']['spaces_in_tags']
        self._conversion_settings.split_tags = self['meta_data_options']['split_tags']
        self._conversion_settings.first_row_as_header = self['table_options']['first_row_as_header']
        self._conversion_settings.first_column_as_header = self['table_options']['first_column_as_header']
        self._conversion_settings.source = self['file_options']['source']
        self._conversion_settings.export_folder_name = self['file_options']['export_folder_name']
        self._conversion_settings.attachment_folder_name = self['file_options']['attachment_folder_name']
        self._conversion_settings.creation_time_in_exported_file_name = \
            self['file_options']['creation_time_in_exported_file_name']

    def __write_config_file(self):
        with open(self._config_file, 'w') as config_file:
            self.write(config_file)
            self.logger.info("Saving configuration file")

    def __read_config_file(self):
        """
        Read config file. If file is missing generate a new one.

        If config file is missing generate a ConversionSettings child object for the default conversion value
        and use that to generate a config data set.

        """
        self.logger.debug('reading config file')
        path = Path(self._config_file)
        if path.is_file():
            self.read(self._config_file)
            self.logger.info(f'Data read from INI file is {self.__repr__()}')
        else:
            self.logger.info('config.ini missing, generating new file and settings set to default.')
            if not self.conversion_settings.silent:
                print("config.ini missing, generating new file.")
            self.conversion_settings = self._default_quick_setting

    def load_and_save_config_from_conversion_quick_setting_string(self, setting):
        """
        Generate a config data set and save the updated config file using a 'setting' value provided as a string
        that uses a default configuration by generating a child class of ConversionSettings and using that object
        to set the config values.

        Parameters
        ----------
        setting
            string: A key 'quick setting' value

        """
        self._conversion_settings = conversion_settings.please.provide(setting)
        self.__load_and_save_settings()

    def load_and_save_config_from_conversion_settings_obj(self, settings: ConversionSettings):
        """
        Generate a config data set and save updtaed config file
        Parameters
        ----------
        settings
            ConversionSettings: A child of the class ConversionSettings

        """
        self._conversion_settings = settings
        self.__load_and_save_settings()

    def __load_and_save_settings(self):
        """
        Read a dictionary of config data, formatted for config file generation and store the new config file.

        """
        self.__wipe_current_config()
        self.read_dict(self.__generate_conversion_dict())
        self.logger.info(f"Quick setting {self['quick_settings']['quick_setting']} loaded")
        self.__write_config_file()

    def __wipe_current_config(self):
        """
        Wipe the current config sections.

        When using read_dict new sections are added to the end of the current config. so when written to file they
        are out of place compared to the validation data.  This method is here to save having to manually delete the
        ini file when coding changes to the conversion dict.  That means it is here to save me having to remember to
        delete the ini file :-)
        """
        for section, keys in self._validation_values.items():
            self.remove_section(section)
        pass

    def __generate_conversion_dict(self):
        """

        Returns
        -------
        Dict
            Dictionary, formatted for config file creation, using values from a ConversionSettings object

        """
        # comments are treated as 'values' with no value (value is set to None) i.e. they are dict entries
        # where the key is the #comment string and the value is None
        return {
            'execution_mode': {
                '    # silent mode stops any output to the command line during execution': None,
                '    # and disables the interactive command line interface.  True or False': None,
                'silent': False
            },
            'conversion_inputs': {
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_conversion_inputs)}': None,
                '    #  nsx = synology Note Station Export file': None,
                '    #  html = simple html based notes pages, no complex CSS or html code': None,
                '    #  markdown =  text files in markdown format': None,
                'conversion_input': self._conversion_settings.conversion_input
            },
            'markdown_conversion_inputs': {
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_markdown_conversion_inputs)}': None,
                'markdown_conversion_input': self._conversion_settings.markdown_conversion_input
            },
            'quick_settings': {
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_export_formats)}': None,
                '    # use manual to use manual settings below': None,
                '    # NOTE if an option other than - manual - is used the rest of the ': None,
                '    # settings in this file will be set automatically': None,
                '    #': None,
                "quick_setting": self._conversion_settings.quick_setting,
                '    # ': None,
                '    # The following sections only apply if the above is set to manual': None,
                '    #  ': None
            },
            'export_formats': {
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_export_formats)}': None,
                "export_format": self._conversion_settings.export_format
            },
            'meta_data_options': {
                '    # Note if front_matter_format sets the presence and type of a section with metadata ': None,
                '    #retrieved from the source': None,
                f'    # Valid entries are {", ".join(self._conversion_settings.valid_front_matter_formats)}': None,
                '    # no entry will result in no front matter section': None,
                'metadata_front_matter_format': self._conversion_settings.front_matter_format,
                '    # metadata schema is a comma separated list of metadata keys that you wish to ': None,
                '    # restrict the retrieved metadata keys. for example ': None,
                '    # title, tags    will return those two if they are found': None,
                '    # If left blank any meta data found will be used': None,
                '    # The available keys in an nsx file are title, ctime, mtime, tag': None,
                'metadata_schema': ",".join(self._conversion_settings.metadata_schema),
                '    # tag prefix is a character you wish to be added to the front of any tag values ': None,
                '    # retrieved from metadata.  NOTE only used if front_matter_format is none': None,
                'tag_prefix': self._conversion_settings.tag_prefix,
                '    # spaces_in_tags if True will maintain spaces in tag words, if False spaces are replaced by a dash -': None,
                'spaces_in_tags': self._conversion_settings.spaces_in_tags,
                '    # split tags will split grouped tags into individual tags if True': None,
                '    # "Tag1", "Tag1/Sub Tag2"  will become "Tag1", "Sub Tag2"': None,
                'split_tags': self._conversion_settings.split_tags
            },
            'table_options': {
                '  #  These two options apply to NSX files ONLY': None,
                'first_row_as_header': self._conversion_settings.first_row_as_header,
                'first_column_as_header': self._conversion_settings.first_column_as_header
            },
            'file_options': {
                'source': self._conversion_settings.source,
                'export_folder_name': self._conversion_settings.export_folder_name,
                'attachment_folder_name': self._conversion_settings.attachment_folder_name,

                'creation_time_in_exported_file_name': self._conversion_settings.creation_time_in_exported_file_name,
                '    # creation time in file name only applies to NSX files.': None,
                '    # If True creation time will be added as prefix to file name': None
            }
        }

    def __str__(self):
        display_dict = str({section: dict(self[section]) for section in self.sections()})
        return str(f'{self.__class__.__name__}{display_dict}')

    def __repr__(self):
        display_dict = str({section: dict(self[section]) for section in self.sections()})
        return str(f'{self.__class__.__name__}{display_dict}')


if __name__ == '__main__':
    # for testing
    my_config = ConfigData('config.ini', 'gfm', allow_no_value=True)
    # my_config.conversion_settings = 'test.py'
    # my_config.conversion_settings = True
    # my_config.write_config_file()
    # my_config.default_config.set_quick_set_settings("gfm")
    # my_config.write_config_file()
    # my_config.read_config_file()
    print("Done")

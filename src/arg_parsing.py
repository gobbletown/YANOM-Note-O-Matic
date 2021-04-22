import argparse
import os
from globals import VERSION
import quick_settings
import logging
import inspect
from globals import APP_NAME


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class CommandLineParsing:
    """
    Read command line arguments, and generate conversion settings based on these values

    """
    def __init__(self):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._parser = argparse.ArgumentParser(description="YANOM Note-O-Matic notes convertor")
        self.__configure_parser()
        self.logger.info("Parsing command line arguments")
        self._args = self._parser.parse_args()
        self.logger.info(f"command line arguments are {self._args}")
        self._conversion_setting = quick_settings.please.provide('manual')

    @property
    def conversion_setting(self):
        return self._conversion_setting

    @property
    def args(self):
        return vars(self._args)

    def __configure_parser(self):
        """Define the command line arguments"""

        self._parser.add_argument('-v', '--version', action='version', version='%(prog)s Version {}'.format(VERSION))
        self._parser.add_argument("-s", "--silent", action="store_true",
                                  help="No output to console. No interactive command line interface for settings.")
        self._parser.add_argument('--source', nargs='?', default=os.getcwd(),
                                  help='Sub directory of current directory containing one or more files to process, '
                                       'or the name of a single file.  '
                                       'For example "my_html_file.html" or "my_nsx_files".  '
                                       'If not provided will search and use current folder AND any sub folders.')
        group = self._parser.add_argument_group('Mutually exclusive options. ',
                                                'To use the interactive command line tool for settings '
                                                'DO NOT use -s or -i')
        settings_from_group = group.add_mutually_exclusive_group()
        settings_from_group.add_argument("-i", "--ini", action="store_true",
                                         help="Use config.ini for conversion settings.")
        settings_from_group.add_argument("-c", "--cli", action="store_true",
                                         help="Use interactive command line interface to choose options and settings. This is the default if no argument is provided.")


if __name__ == '__main__':
    args = CommandLineParsing()
    print(args.args)
    print(args.conversion_setting)

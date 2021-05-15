import distutils.version
import logging
import os
import shutil
import subprocess
import sys

import config


def what_module_is_this():
    return __name__


class PandocConverter:
    def __init__(self, conversion_settings):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self.conversion_settings = conversion_settings
        self.output_file_format = self.conversion_settings.export_format
        self.pandoc_version = None
        self.pandoc_conversion_options = {'q_own_notes': 'markdown_strict+pipe_tables-raw_html',
                                          'gfm': 'gfm',
                                          'obsidian': 'gfm',
                                          'pandoc_markdown': 'markdown',
                                          'commonmark': 'commonmark',
                                          'pandoc_markdown_strict': 'markdown_strict',
                                          'multimarkdown': 'markdown_mmd',
                                          'html': 'html'}
        self.pandoc_options = None
        self.check_pandoc_is_installed_if_not_exit_program()
        self.find_pandoc_version()
        self.generate_pandoc_options()

    def find_pandoc_version(self):
        try:
            self.pandoc_version = subprocess.run(['pandoc', '-v'], capture_output=True, text=True, timeout=3)
            self.pandoc_version = self.pandoc_version.stdout[7:].split('\n', 1)[0].strip()
            if not config.silent:
                print('Found pandoc ' + str(self.pandoc_version))
            self.logger.debug(f"Found pandoc version {str(self.pandoc_version)}")

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Exiting as unable to find pandoc\n{e}")
            if not config.silent:
                print("Unable to locate pandoc please check pandoc installation and see *.log files.")
                print("Exiting.")
            sys.exit(0)

    def generate_pandoc_options(self):
        self.logger.debug(
            f"Pandoc configured for export format - '{self.pandoc_conversion_options[self.output_file_format]}'")
        input_format = self.calculate_input_format()
        self.pandoc_options = ['pandoc', '-f', input_format, '-s', '-t',
                               self.pandoc_conversion_options[self.output_file_format]]

        if self.pandoc_older_than_v_1_16():
            self.pandoc_options = self.pandoc_options + ['--no-wrap']
            return

        if self.pandoc_older_than_v_1_19():
            self.pandoc_options = ['--wrap=none', '-o']
            return

        if self.pandoc_older_than_v_2_11_2():
            self.pandoc_options = ['--wrap=none', '--atx-headers']
            return

        self.pandoc_options = self.pandoc_options + ['--wrap=none', '--markdown-headings=atx']

    def calculate_input_format(self):
        if self.conversion_settings.conversion_input == 'nsx' or self.conversion_settings.conversion_input == 'html':
            return 'html'
        if self.conversion_settings.conversion_input == 'markdown':
            return self.pandoc_conversion_options[self.conversion_settings.markdown_conversion_input]

    def convert_using_strings(self, input_data, name):
        try:
            out = subprocess.run(self.pandoc_options, input=input_data, capture_output=True,
                                 encoding='utf-8', text=True, timeout=20)
            if out.returncode > 0:
                self.logger.error(f"Pandoc Return code={out.returncode}, error={out.stderr}")
            return out.stdout
        except subprocess.CalledProcessError:
            self.logger.error(f"Unable to convert note {name}")
            self.error_handling(name)

        return 'Error converting data'

    def pandoc_older_than_v_1_16(self):
        return distutils.version.LooseVersion(self.pandoc_version) < distutils.version.LooseVersion('1.16')

    def pandoc_older_than_v_1_19(self):
        return distutils.version.LooseVersion(self.pandoc_version) < distutils.version.LooseVersion('1.19')

    def pandoc_older_than_v_2_11_2(self):
        return distutils.version.LooseVersion(self.pandoc_version) < distutils.version.LooseVersion('2.11.2')

    def check_pandoc_is_installed_if_not_exit_program(self):
        if not shutil.which('pandoc') and not os.path.isfile('pandoc'):
            logging.info("Pandoc program not found - exiting")
            if not config.silent:
                print("Can't find pandoc. Please install pandoc or place it to the directory, where the script is.")
            sys.exit(1)

    def error_handling(self, note_title):
        msg = f"Error converting note {note_title} for pandoc please check nsx_converter.log and pandoc installation."
        logging.error(msg)
        if not config.silent:
            print(msg)
            print("Attempting to continue...")

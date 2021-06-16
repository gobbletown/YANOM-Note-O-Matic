from packaging import version
import logging
from pathlib import Path
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
        self._pandoc_version = None
        self.pandoc_conversion_options = {'q_own_notes': 'markdown_strict+pipe_tables-raw_html',
                                          'gfm': 'gfm',
                                          'obsidian': 'gfm',
                                          'pandoc_markdown': 'markdown',
                                          'commonmark': 'commonmark',
                                          'pandoc_markdown_strict': 'markdown_strict',
                                          'multimarkdown': 'markdown_mmd',
                                          'html': 'html'}
        self.pandoc_options = None
        self._pandoc_path = None
        self.set_pandoc_path()
        self.check_and_set_pandoc_options_if_required()

    @staticmethod
    def is_system_linux():
        return sys.platform.startswith('linux')

    @staticmethod
    def is_this_a_frozen_package():
        return getattr(sys, 'frozen', False)

    def set_pandoc_path(self):
        if self.is_this_a_frozen_package() and not self.is_system_linux():
            self._pandoc_path = str(Path(self.conversion_settings.working_directory, 'pandoc/pandoc'))
            return

        self._pandoc_path = 'pandoc'

    def check_and_set_pandoc_options_if_required(self):
        # Early returns for conversion not needing pandoc
        if self.conversion_settings.conversion_input == 'nsx' and self.conversion_settings.export_format == 'html':
            return
        if self.conversion_settings.conversion_input == 'html' and self.conversion_settings.export_format == 'html':
            return
        if self.conversion_settings.conversion_input == 'markdown' \
                and (self.conversion_settings.markdown_conversion_input == self.conversion_settings.export_format):
            return

        self.find_pandoc_version()
        self.generate_pandoc_options()

    def find_pandoc_version(self):
        try:
            self._pandoc_version = subprocess.run([self._pandoc_path, '-v'], capture_output=True, text=True, timeout=3)
            self._pandoc_version = self._pandoc_version.stdout[7:].split('\n', 1)[0].strip()
            if not config.silent:
                print('Found pandoc ' + str(self._pandoc_version))
            self.logger.debug(f"Found pandoc version {str(self._pandoc_version)} at {self._pandoc_path}")

        except subprocess.CalledProcessError as exc:
            self.logger.warning(f"Exiting as unable to get pandoc version\n{exc}")
            if not config.silent:
                print("Unable to fetch pandoc version please check log files for additional information.")
                print("Exiting.")
            sys.exit(1)

    def generate_pandoc_options(self):
        self.logger.debug(
            f"Pandoc configured for export format - '{self.pandoc_conversion_options[self.output_file_format]}'")
        input_format = self._calculate_input_format()
        self.pandoc_options = [self._pandoc_path, '-f', input_format, '-s', '-t',
                               self.pandoc_conversion_options[self.output_file_format]]

        if self._pandoc_older_than_v_1_16():
            self.pandoc_options = self.pandoc_options + ['--no-wrap']
            return

        if self._pandoc_older_than_v_1_19():
            self.pandoc_options = ['--wrap=none', '-o']
            return

        if self._pandoc_older_than_v_2_11_2():
            self.pandoc_options = ['--wrap=none', '--atx-headers']
            return

        self.pandoc_options = self.pandoc_options + ['--wrap=none', '--markdown-headings=atx']

    def _calculate_input_format(self):
        if self.conversion_settings.conversion_input == 'nsx' or self.conversion_settings.conversion_input == 'html':
            return 'html'
        # if not nsx or html must be markdown
        return self.pandoc_conversion_options[self.conversion_settings.markdown_conversion_input]

    def convert_using_strings(self, input_data, note_title):
        try:
            out = subprocess.run(self.pandoc_options, input=input_data, capture_output=True,
                                 encoding='utf-8', text=True, timeout=20)
            if out.returncode > 0:
                self.logger.error(f"Pandoc Return code={out.returncode}, error={out.stderr}")
            return out.stdout

        except subprocess.CalledProcessError as exc:
            self.logger.error(f"Unable to convert note {note_title}. Pandoc error - {exc}")
            if not config.silent:
                print(f"Error converting note {note_title} with pandoc please check log file and pandoc installation.")
                print("Attempting to continue...")

        return 'Error converting data'

    def _pandoc_older_than_v_1_16(self):
        return version.parse(self._pandoc_version) < version.parse('1.16')

    def _pandoc_older_than_v_1_19(self):
        return version.parse(self._pandoc_version) < version.parse('1.19')

    def _pandoc_older_than_v_2_11_2(self):
        return version.parse(self._pandoc_version) < version.parse('2.11.2')



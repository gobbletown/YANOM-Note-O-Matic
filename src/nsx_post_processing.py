import logging

import config
from iframe_processing import post_process_iframes_to_markdown
from image_processing import ObsidianImageTagFormatter


def what_module_is_this():
    return __name__


class NoteStationPostProcessing:
    def __init__(self, note):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._note = note
        self._conversion_settings = note.conversion_settings
        self._yaml_header = ''
        self._post_processed_content = note.converted_content
        self._pre_processor = note.pre_processor
        self.post_process_note_page()

    def post_process_note_page(self):
        if self._conversion_settings.front_matter_format != 'none':
            self._add_meta_data()
        self._add_check_lists()
        if self._note.conversion_settings.export_format != 'pandoc_markdown_strict':
            self._add_iframes()
        self._format_images_links()
        self._add_one_last_line_break()

    def _add_meta_data(self):
        self.logger.debug(f"Adding meta-data to page")
        self._post_processed_content = self._pre_processor.metadata_processor.add_metadata_md_to_content(self._post_processed_content)

    def _add_check_lists(self):
        if self._note.pre_processor.checklist_processor.list_of_checklist_items:
            self.logger.debug(f"Adding checklists to page")
            self._post_processed_content = self._note.pre_processor.checklist_processor.add_checklist_items_to(self._post_processed_content)

    def _add_iframes(self):
        if self._pre_processor.iframes_dict:
            self.logger.debug(f"Adding iframes to note page")
            self._post_processed_content = post_process_iframes_to_markdown(self._post_processed_content, self._pre_processor.iframes_dict)

    def _format_images_links(self):
        if self._conversion_settings.export_format == 'obsidian':
            self.logger.debug(f"Formatting image links for Obsidian")
            obsidian_image_link_formatter = ObsidianImageTagFormatter(self._post_processed_content, 'obsidian')
            self._post_processed_content = obsidian_image_link_formatter.processed_content

    def _add_one_last_line_break(self):
        self._post_processed_content = f'{self._post_processed_content}\n'

    @property
    def post_processed_content(self):
        return self._post_processed_content

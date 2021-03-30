from checklist_processing import HTMLInputMDOutputChecklistProcessor
from file_converter_abstract import FileConverter
from metadata_processing import MetaDataProcessor


class HTMLToMDConverter(FileConverter):
    def pre_process_content(self):
        self._checklist_processor = HTMLInputMDOutputChecklistProcessor(self._file_content)
        self._pre_processed_content = self._checklist_processor.processed_html
        self._pre_processed_content = self.update_note_links(self._pre_processed_content, 'html', 'md')
        self.parse_metadata_if_required()

    def parse_metadata_if_required(self):
        if self._conversion_settings.export_format == 'pandoc_markdown':
            return

        self._metadata_processor = MetaDataProcessor(self._conversion_settings)
        self._metadata_processor.parse_html_metadata(self._pre_processed_content)

    def post_process_content(self):
        self._post_processed_content = self._converted_content
        self.post_process_obsidian_image_links_if_required()
        self.add_check_lists()
        self.add_meta_data_if_required()
        self.add_one_last_line_break()

    def add_check_lists(self):
        self._post_processed_content = self._checklist_processor.add_checklist_items_to(self._post_processed_content)

    def add_one_last_line_break(self):
        self._post_processed_content = f'{self._post_processed_content}\n'

    def add_meta_data_if_required(self):
        if self._conversion_settings.export_format == 'pandoc_markdown':
            return

        self._post_processed_content = self._metadata_processor.add_metadata_md_to_content(self._post_processed_content)

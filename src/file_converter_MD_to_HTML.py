from file_converter_abstract import FileConverter
from metadata_processing import MetaDataProcessor


class MDToHTMLConverter(FileConverter):
    def pre_process_content(self):
        self._pre_processed_content = self._file_content
        self.parse_metadata_if_required()
        self.pre_process_obsidian_image_links_if_required()
        self.rename_target_file_if_already_exists()

    def parse_metadata_if_required(self):
        if not self._conversion_settings.markdown_conversion_input == 'pandoc_markdown':
            self._metadata_processor = MetaDataProcessor(self._conversion_settings)
            self._pre_processed_content = self._metadata_processor.parse_md_metadata(self._pre_processed_content)

    def post_process_content(self):
        self._post_processed_content = self._converted_content
        self._post_processed_content = self.update_note_links(self._post_processed_content, 'md', 'html')
        self.add_meta_data_if_required()

    def add_meta_data_if_required(self):
        if self._conversion_settings.markdown_conversion_input == 'pandoc_markdown':
            return

        self._post_processed_content = self._metadata_processor.add_metadata_html_to_content(self._post_processed_content)

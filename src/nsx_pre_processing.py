from abc import ABC, abstractmethod
import logging
import re


from chart_processing import NSXChartProcessor
from checklist_processing import NSXInputMDOutputChecklistProcessor, NSXInputHTMLOutputChecklistProcessor
import config
from helper_functions import add_strong_between_tags, change_html_tags
from iframe_processing import pre_process_iframes_from_html
from image_processing import ImageTag
from metadata_processing import MetaDataProcessor
from sn_attachment import FileNSAttachment
from sn_inter_note_link_processing import SNLinksToOtherNotes


def what_module_is_this():
    return __name__


class PreProcessing(ABC):
    """Abstract class representing a pre conversion note formatting """

    @abstractmethod
    def pre_process_note_page(self):  # pragma: no cover
        pass


class NoteStationPreProcessing(PreProcessing):
    """
    Main driver for pre-processing of synology html note data.

    Clean and format data for pandoc.  Also regenerate html checklists or put in place holders to aid adding checklists
    back in markdown files after pandoc processing.
    """

    def __init__(self, note):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._note = note
        self._pre_processed_content = note.raw_content
        self._attachments = note.attachments
        self._image_attachments = []
        self._image_tags = {}
        self._image_tag_processors = []
        self._image_ref_to_image_path = {}
        self._iframes_dict = {}
        self._checklist_processor = None
        self._charts = []
        self._metadata_processor = None
        self.pre_process_note_page()
        pass

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @pre_processed_content.setter
    def pre_processed_content(self, content):
        self._pre_processed_content = content

    @property
    def metadata_processor(self):
        return self._metadata_processor

    @property
    def checklist_processor(self):
        return self._checklist_processor

    @property
    def iframes_dict(self):
        return self._iframes_dict

    def pre_process_note_page(self):
        self.logger.debug(f"Pre processing of note page {self._note.title}")
        self._create_image_tag_processors()
        self._update_content_with_new_img_tags()
        if self._note.conversion_settings.export_format != 'pandoc_markdown_strict' \
                and self._note.conversion_settings.export_format != 'html':
            self._process_iframes()
        self._fix_ordered_list()
        self._fix_unordered_list()
        self._fix_check_lists()
        self._add_boarder_to_tables()
        if self._note.conversion_settings.first_row_as_header:
            self._fix_table_headers()
        if self._note.conversion_settings.first_column_as_header:
            self._first_column_in_table_as_header_if_required()
        self._extract_and_generate_chart()
        if self._note.conversion_settings.front_matter_format != 'none':
            self._generate_metadata()
        self._generate_links_to_other_note_pages()
        self._add_file_attachment_links()
        self._clean_excessive_divs()

    def _process_iframes(self):
        self.pre_processed_content, self._iframes_dict = pre_process_iframes_from_html(self.pre_processed_content)

    def _create_image_tag_processors(self):
        self.logger.debug(f"Cleaning image tags")
        raw_image_tags = re.findall('<img class=[^>]*syno-notestation-image-object[^>]*src=[^>]*ref=[^>]*>',
                                    self._pre_processed_content)
        self._image_tag_processors = [ImageTag(tag, self._attachments) for tag in raw_image_tags]

    def _update_content_with_new_img_tags(self):
        for image_tag_processor in self._image_tag_processors:
            self._pre_processed_content = self._pre_processed_content.replace(image_tag_processor.raw_tag,
                                                                              image_tag_processor.processed_tag)

    def _clean_excessive_divs(self):
        """
        Replace all the div's with p's
        """
        self.logger.debug(f"Cleaning html <div")
        self._pre_processed_content = self._pre_processed_content.replace('<div></div>', '<p></p>')
        self._pre_processed_content = self._pre_processed_content.replace('<div', '<p')
        self._pre_processed_content = self._pre_processed_content.replace('</div', '</p')

    def _fix_ordered_list(self):
        self.logger.debug(f"Cleaning number lists")
        self._pre_processed_content = self._pre_processed_content.replace('</li><ol><li>', '<ol><li>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ol><li>', '</li></ol></li><li>')

    def _fix_unordered_list(self):
        self.logger.debug(f"Cleaning bullet lists")
        self._pre_processed_content = self._pre_processed_content.replace('</li><ul><li>', '<ul><li>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ul><li>', '</li></ul></li><li>')

    def _fix_check_lists(self):
        self.logger.debug(f"Cleaning check lists")

        if self._note.conversion_settings.export_format == 'html':
            self._checklist_processor = NSXInputHTMLOutputChecklistProcessor(self._pre_processed_content)
        else:
            self._checklist_processor = NSXInputMDOutputChecklistProcessor(self._pre_processed_content)

        self._pre_processed_content = self._checklist_processor.processed_html
        pass

    def _extract_and_generate_chart(self):
        self.logger.debug(f"Cleaning charts")

        chart_options = {'create_image': self._note._conversion_settings.chart_image,
                         'create_csv': self._note._conversion_settings.chart_csv,
                         'create_data_table': self._note._conversion_settings.chart_data_table,
                         }
        chart_processor = NSXChartProcessor(self._note, self._pre_processed_content, **chart_options)

        self._pre_processed_content = chart_processor.processed_html

    def _fix_table_headers(self):
        self.logger.debug(f"Cleaning table headers")
        tables = re.findall('<table.*</table>', self._pre_processed_content)

        for table in tables:
            new_table = table
            new_table = new_table.replace('<b>', '<strong>')
            new_table = new_table.replace('</b>', '</strong>')
            new_table = new_table.replace('<tbody>', '<thead>')
            new_table = new_table.replace('</td></tr>', '</td></tr></thead><tbody>', 1)
            self._pre_processed_content = self._pre_processed_content.replace(table, new_table)

    def _first_column_in_table_as_header_if_required(self):
        self.logger.debug(f"Make tables first column bold")
        tables = re.findall('<table.*</table>', self._pre_processed_content)

        for table in tables:
            new_table = add_strong_between_tags('<tr><td>', '</td><td>', table)
            new_table = change_html_tags('<tr><td>', '</td>', '<tr><th>', '</th>', new_table)
            self._pre_processed_content = self._pre_processed_content.replace(table, new_table)

    def _add_boarder_to_tables(self):
        self.logger.debug(f"Adding boarders to tables")
        tables = re.findall('<table.*</table>', self._pre_processed_content)

        for table in tables:
            new_table = table
            new_table = new_table.replace('<table', '<table border="1"')
            self._pre_processed_content = self._pre_processed_content.replace(table, new_table)

    def _generate_metadata(self):
        self.logger.debug(f"Generating meta-data")
        self._metadata_processor = MetaDataProcessor(self._note.conversion_settings)
        self._metadata_processor.parse_dict_metadata(self._note.note_json)
        self._pre_processed_content = f'<head><title> </title></head>{self._pre_processed_content}'
        self._pre_processed_content = self._metadata_processor.add_metadata_html_to_content(self._pre_processed_content)

    def _generate_links_to_other_note_pages(self):
        self.logger.debug(f"Creating links between pages")
        link_generator = SNLinksToOtherNotes(self._note, self._pre_processed_content, self._note.nsx_file)
        self.pre_processed_content = link_generator.content

    def _add_file_attachment_links(self):
        self.logger.debug(f"Add attachment links to page content")
        attachments = [attachment
                       for attachment in self._note.attachments.values()
                       if type(attachment) is FileNSAttachment
                       ]
        if attachments:
            self.pre_processed_content = f'{self.pre_processed_content}<h6>Attachments</h6>'
            for attachment in attachments:
                self.pre_processed_content = f'{self.pre_processed_content}<p>{attachment.html_link}</p>'

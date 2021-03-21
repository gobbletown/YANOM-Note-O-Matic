import re
from abc import ABC, abstractmethod
from sn_attachment import ChartStringNSAttachment, ChartImageNSAttachment
from chart_processing import NSChart
import logging
from globals import APP_NAME
import inspect
from helper_functions import add_strong_between_tags, change_html_tags
from sn_attachment import FileNSAttachment
from src.image_processing import ImageTag
from src.inter_note_link_processing import SNLinksToOtherNotes
from src.metadata_processing import NSMetaDataGenerator


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class CheckListItem(ABC):
    def __init__(self, raw_item_html):
        self._raw_item_html = raw_item_html
        self._processed_item = str
        self._item_checked = False
        self._item_text = str
        self._check_list_level = 1
        self.find_item_text()
        self.find_status()
        self.find_item_level()
        self.build_processed_item()

    @property
    def raw_item_html(self):
        return self._raw_item_html

    @property
    def processed_item(self):
        return self._processed_item

    @property
    def check_list_level(self):
        return self._check_list_level

    @check_list_level.setter
    def check_list_level(self, value):
        self._check_list_level = value

    @abstractmethod
    def build_processed_item(self):
        pass

    def find_item_text(self):
        matches = re.findall('<input type="checkbox"[^>]*>([^<]*)', self._raw_item_html)
        self._item_text = matches[0]

    @abstractmethod
    def find_status(self):
        pass

    @abstractmethod
    def find_item_level(self):
        pass


class NSCheckListItem(CheckListItem):
    def build_processed_item(self):
        pass

    def find_item_text(self):
        matches = re.findall('<input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>([^<]*)',
                             self._raw_item_html)
        self._item_text = matches[0]

    def find_status(self):
        matches = re.findall('syno-notestation-editor-checkbox-checked', self._raw_item_html)
        if matches:
            self._item_checked = True

    def find_item_level(self):
        matches = re.findall('[0-9]{2}', self._raw_item_html)
        if matches:
            indent = int(matches[0])
            self._check_list_level = indent // 30


class GenerateNSMarkdownCheckListItem(NSCheckListItem):
    def build_processed_item(self):
        tabs = '\t' * self._check_list_level
        checked = ' '
        if self._item_checked:
            checked = 'x'

        self._processed_item = f"{tabs}- [{checked}] {self._item_text}"


class GenerateNSHTMLCheckListItem(NSCheckListItem):
    def build_processed_item(self):
        indent = self._check_list_level * 30
        checked = ''
        if self._item_checked:
            checked = 'checked'

        self._processed_item = f'<p style="padding-left: {indent}px;"><input type="checkbox" {checked}/>{self._item_text}</p> '


class PreProcessing(ABC):
    """Abstract class representing a pre conversion note formatting """

    @abstractmethod
    def pre_process_note_page(self):
        pass


class NoteStationPreProcessing(PreProcessing):
    """
    Main driver for pre-processing of synology html note data.

    Clean and format data for pandoc.  Also regenerate html checklists or put in place holders to aid adding checklists
    back in markdown files after pandoc processing.
    """

    def __init__(self, note):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._note = note
        self._pre_processed_content = note.raw_content
        self._attachments = note.attachments
        self._image_attachments = []
        self._image_tags = {}
        self._image_tag_processors = []
        self._image_ref_to_image_path = {}
        self._check_list_items = {}
        self._charts = []
        self._header_generator = None
        self.pre_process_note_page()
        pass

    @property
    def pre_processed_content(self):
        return self._pre_processed_content

    @property
    def header_generator(self):
        return self._header_generator

    @property
    def check_list_items(self):
        return self._check_list_items

    @pre_processed_content.setter
    def pre_processed_content(self, content):
        self._pre_processed_content = content

    def pre_process_note_page(self):
        self.logger.info(f"Pre processing of note page {self._note.title}")
        self.__create_image_tag_processors()
        self.__update_content_with_new_img_tags()
        self.__clean_excessive_divs()
        self.__fix_ordered_list()
        self.__fix_unordered_list()
        self.__fix_check_lists()
        self.__add_boarder_to_tables()
        if self._note.conversion_settings.first_row_as_header:
            self.__fix_table_headers()
        if self._note.conversion_settings.first_column_as_header:
            self.__first_column_in_table_as_header_if_required()
        self.__extract_and_generate_chart()
        if self._note.conversion_settings.include_meta_data:
            self.__generate_metadata()
        self.__generate_links_to_other_note_pages()
        self.__add_attachment_links()

    def __create_image_tag_processors(self):
        self.logger.info(f"Cleaning image tags")
        raw_image_tags = re.findall('<img class=[^>]*syno-notestation-image-object[^>]*src=[^>]*ref=[^>]*>',
                                    self._pre_processed_content)
        self._image_tag_processors = [ImageTag(tag, self._attachments) for tag in raw_image_tags]

    def __update_content_with_new_img_tags(self):
        for image_tag_processor in self._image_tag_processors:
            self._pre_processed_content = self._pre_processed_content.replace(image_tag_processor.raw_tag,
                                                                              image_tag_processor.processed_tag)

    def __clean_excessive_divs(self):
        """
        Replace all the div's with p's
        """
        self.logger.info(f"Cleaning html <div")
        self._pre_processed_content = self._pre_processed_content.replace('<div></div>', '<p></p>')
        self._pre_processed_content = self._pre_processed_content.replace('<div', '<p')
        self._pre_processed_content = self._pre_processed_content.replace('</div', '</p')

    def __fix_ordered_list(self):
        self.logger.info(f"Cleaning number lists")
        self._pre_processed_content = self._pre_processed_content.replace('</li><ol>', '<ol>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ol>', '</li></li></ol>')

    def __fix_unordered_list(self):
        self.logger.info(f"Cleaning bullet lists")
        self._pre_processed_content = self._pre_processed_content.replace('</li><ul>', '<ul>')
        self._pre_processed_content = self._pre_processed_content.replace('</li></ul>', '</li></li></ul>')

    def __generate_dict_of_checklist_generators(self, raw_checklists_items):
        if self._note.conversion_settings.export_format == 'html':
            check_list_items = [GenerateNSHTMLCheckListItem(item) for item in raw_checklists_items]
        else:
            check_list_items = [GenerateNSMarkdownCheckListItem(item) for item in raw_checklists_items]

        self._check_list_items = {id(item): item for item in check_list_items}

    def __add_checklists_to_pre_processed_content(self):
        if self._note.conversion_settings.export_format == 'html':
            for item in self._check_list_items.values():
                # For html export replace synology html with newly generated html
                self._pre_processed_content = self._pre_processed_content.replace(item.raw_item_html,
                                                                                  item.processed_item)
            return

        for item in self._check_list_items.values():
            # Using 'check-list-id(item)' as a checklist item place holder as pandoc cannot convert checklists,
            # the unique id will be used to replace the id with good checklist items in post processing.
            self._pre_processed_content = self._pre_processed_content.replace(item.raw_item_html,
                                                                              f'check-list-{str(id(item))}<br/>')

    def __fix_check_lists(self):
        self.logger.info(f"Cleaning check lists")

        raw_checklists_items = re.findall(
            '<p[^>]*><input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>[^<]*</p>',
            self._pre_processed_content)

        self.__generate_dict_of_checklist_generators(raw_checklists_items)

        self.__add_checklists_to_pre_processed_content()

    def __extract_and_generate_chart(self):
        self.logger.info(f"Cleaning charts")
        raw_charts_html = re.findall('<p[^>]*><p class=[^>]*syno-ns-chart-object[^>]*></p>',
                                     self._pre_processed_content)

        if raw_charts_html:
            self._charts = {NSChart(raw_chart): raw_chart for raw_chart in raw_charts_html}

            for chart, raw_chart_html in self._charts.items():
                self.__generate_csv_attachment(chart)
                self.__generate_png_attachment(chart)
                self.__replace_raw_chart_html_with_pre_processed_html(chart, raw_chart_html)

    def __generate_csv_attachment(self, chart):
        self._note.attachments[f"{id(chart)}.csv"] = ChartStringNSAttachment(self._note, f"{id(chart)}.csv",
                                                                             chart.csv_chart_data_string)
        self._note.attachment_count += 1

    def __generate_png_attachment(self, chart):
        self._note.attachments[f"{id(chart)}.png"] = ChartImageNSAttachment(self._note, f"{id(chart)}.png",
                                                                            chart.png_img_buffer)
        self._note.image_count += 1

    def __generate_replacement_html(self, chart):
        return f"<p>{self._note.attachments[f'{id(chart)}.png'].html_link}</p>" \
               f"<p>{self._note.attachments[f'{id(chart)}.csv'].html_link}</p>" \
               f"<p>{chart.html_chart_data_table}</p>"

    def __replace_raw_chart_html_with_pre_processed_html(self, chart, raw_charts_html):
        replacement_html = self.__generate_replacement_html(chart)
        self.pre_processed_content = self.pre_processed_content.replace(raw_charts_html, replacement_html)

    def __fix_table_headers(self):
        self.logger.info(f"Cleaning table headers")
        tables = re.findall('<table.*</table>', self._pre_processed_content)

        for table in tables:
            new_table = table
            new_table = new_table.replace('<b>', '<strong>')
            new_table = new_table.replace('</b>', '</strong>')
            new_table = new_table.replace('<tbody>', '<thead>')
            new_table = new_table.replace('</td></tr>', '</td></tr></thead><tbody>', 1)
            self._pre_processed_content = self._pre_processed_content.replace(table, new_table)

    def __first_column_in_table_as_header_if_required(self):
        self.logger.info(f"Make tables first column bold")
        tables = re.findall('<table.*</table>', self._pre_processed_content)

        for table in tables:
            new_table = add_strong_between_tags('<tr><td>', '</td><td>', table)
            new_table = change_html_tags('<tr><td>', '</td>', '<tr><th>', '</th>', new_table)
            self._pre_processed_content = self._pre_processed_content.replace(table, new_table)

    def __add_boarder_to_tables(self):
        tables = re.findall('<table.*</table>', self._pre_processed_content)

        for table in tables:
            new_table = table
            new_table = new_table.replace('<table', '<table border="1"')
            self._pre_processed_content = self._pre_processed_content.replace(table, new_table)

    def __generate_metadata(self):
        self.logger.info(f"Generating meta-data")
        self._header_generator = NSMetaDataGenerator(self._note)
        self._pre_processed_content = f"{self._header_generator.metadata_html}{self._pre_processed_content}"

    def __generate_links_to_other_note_pages(self):
        self.logger.info(f"Creating links between pages")
        link_generator = SNLinksToOtherNotes(self._note, self._pre_processed_content, self._note.nsx_file)
        self.pre_processed_content = link_generator.content

    def __add_attachment_links(self):
        attachments = [attachment
                       for attachment in self._note.attachments.values()
                       if isinstance(attachment, FileNSAttachment)
                       ]
        if attachments:
            self.pre_processed_content = f'{self.pre_processed_content}<h6>Attachments</h6>'
            for attachment in attachments:
                self.pre_processed_content = f'{self.pre_processed_content}<p>{attachment.html_link}</p>'

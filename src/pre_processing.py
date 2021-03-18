import re
from abc import ABC, abstractmethod
from sn_attachment import ImageNSAttachment, ChartStringNSAttachment, ChartImageNSAttachment
from charts import NSChart
import logging
from globals import APP_NAME
import inspect
from helper_functions import add_strong_between_tags, change_html_tags
import time


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class SNLinksToOtherNotes:
    """
    Attempt to create valid links to other notes pages using the link title text.

    Replace html '<a href=' tag links with new links.  Links to new file names are created if the link title matches
    a page name.  If more than one page name matches then link to all matches.  If a link has been renamed and no
    longer matches a page, search links that have already been linked to pages and if the href link value matches
    use those links.

    The links are not guaranteed to be valid/correct but this is currently the best guess for links to other note pages.

    """
    def __init__(self, note_page, content, nsx_file):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._note_page = note_page
        self._content = content
        self._nsx_file = nsx_file
        self._raw_note_links = []
        self._list_of_raw_links = {}
        self._all_note_pages = {}
        self._replacement_links = {}
        self.__generate_dict_of_links()
        if self._list_of_raw_links:
            self.__build_list_of_all_note_pages()
            self.__match_link_title_to_note()
            self.__find_potential_match_for_renamed_links()
            self.__update_content()

    class IntraPageLink:
        """
        Hold details fo, and generate a replacement 'a' tag href link
        """
        def __init__(self, raw_link, note, href_note):
            self._raw_link = raw_link
            self._href_text = ''
            self._href_link_value = re.findall('<a href=\"(.*)\"', raw_link)[0]
            self._new_link = ''
            self._note_page = note
            self._href_note = href_note

            self.__generate_new_link()

        def __generate_new_link(self):
            if self._note_page.parent_notebook == self._href_note.parent_notebook:
                self._new_link = f'<a href="{self._href_note.file_name}">{self._href_note.title}</a>'
            self._new_link = f'<a href="../{self._href_note.notebook_folder_name}/{self._href_note.file_name}">{self._href_note.title}</a>'

        @property
        def new_link(self):
            return self._new_link

        @property
        def href_link_value(self):
            return self._href_link_value

        @property
        def note_page(self):
            return self._note_page

        @property
        def href_note(self):
            return self._href_note

    def __generate_dict_of_links(self):
        self._raw_note_links = re.findall('<a href="notestation://[^>]*>[^>]*>', self._content)

        link_text = []
        for raw_link in self._raw_note_links:
            text_from_link = re.findall('<a href="notestation://[^>]*>([^<]*)</a>', raw_link)
            link_text.append(text_from_link[0])

        self._list_of_raw_links = dict(zip(link_text, self._raw_note_links))

    def __build_list_of_all_note_pages(self):
        self._all_note_pages = [(note.title, note)
                                for note in self._nsx_file.note_pages.values()
                                if not note.parent_notebook == 'recycle_bin'   # ignore items in recycle bin
                                ]

    def __match_link_title_to_note(self):
        for title, link in self._list_of_raw_links.items():
            replacement_links = [self.IntraPageLink(link, self._note_page, title_and_page[1])
                                 for title_and_page in self._all_note_pages
                                 if title == title_and_page[0]]
            if replacement_links:
                self._replacement_links[link] = replacement_links

    def __find_potential_match_for_renamed_links(self):
        for raw_link in self._raw_note_links:
            new_replacement_links = {}
            if raw_link not in self._replacement_links.keys():  # then it is a renamed link
                self.logger.info(f"Attempting to create links for renamed links")
                # search already found replacement links for this links href value and if found give it a new link
                for replacement_links in self._replacement_links.values():
                    if re.findall('<a href=\"(.*)\"', raw_link)[0] == replacement_links[0].href_link_value:
                        new_replacement_links[raw_link] = [self.IntraPageLink(raw_link, self._note_page,
                                                                              replacement_links[0].href_note)]

            # now merge the renamed link replacement link dict into the main replacement_links dict
            self._replacement_links = {**self._replacement_links, **new_replacement_links}

    def __update_content(self):
        for raw_link, replacement_links in self._replacement_links.items():
            self._content = self._content.replace(raw_link, self.__generate_html_code_for_new_links(replacement_links))

    @staticmethod
    def __generate_html_code_for_new_links(links):
        if len(links) == 1:
            return f'{links[0].new_link}'

        html_code = ''
        for link in links:
            html_code = f'{html_code}{link.new_link}<br>'
        return html_code

    @property
    def content(self):
        return self._content


class MetaDataGenerator(ABC):
    def __init__(self, note):
        self._note = note
        self._conversion_settings = note.conversion_settings
        self._metadata_html = ''
        self._metadata_yaml = ''
        self._metadata_text = ''
        self._tags = None

    @abstractmethod
    def generate_metadata(self):
        pass


class NSMetaDataGenerator(MetaDataGenerator):
    def __init__(self, note):
        super().__init__(note)
        self._tags = self._note.json_data["tag"]
        self.generate_metadata()

    def generate_metadata(self):
        self.__add_title_if_required()
        self.__add_creation_time_if_required()
        self.__add_modified_time_if_required()
        self.__remove_tag_spaces_if_required()
        self.__split_tags_if_required()
        self.__add_tags_if_required()
        self._metadata_text = self._metadata_yaml
        self.__add_head_wrapper()

    def __add_title_if_required(self):
        self._metadata_html = f'{self._metadata_html}<meta name="title" content="{self._note.json_data["title"]}">'
        self._metadata_yaml = f'{self._metadata_yaml}title: {self._note.json_data["title"]}\n'

    def __add_creation_time_if_required(self):
        formatted_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(self._note.json_data["ctime"]))
        self._metadata_html = f'{self._metadata_html}<meta name="creation_time" content="{formatted_time}">'
        self._metadata_yaml = f'{self._metadata_yaml}creation_time: {formatted_time}\n'

    def __add_modified_time_if_required(self):
        formatted_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(self._note.json_data["mtime"]))
        self._metadata_html = f'{self._metadata_html}<meta name="modified_time" content="{formatted_time}">'
        self._metadata_yaml = f'{self._metadata_yaml}modified_time: {formatted_time}\n'

    def __remove_tag_spaces_if_required(self):
        if not self._conversion_settings.spaces_in_tags:
            return

        self._tags = [tag.replace(' ', '-') for tag in self._tags]

    def __split_tags_if_required(self):
        if not self._conversion_settings.split_tags:
            return

        set_tags = {tag for tag_split in self._tags for tag in tag_split.split('/')}
        self._tags = [tag for tag in set_tags]

    def __add_tags_if_required(self):
        if not self._conversion_settings.include_tags:
            return

        if not self._tags:
            return

        tag_string = ''
        for tag in self._tags:
            tag_string = f'{tag_string}, {tag}'

        tag_string_for_html = f'"{tag_string[2:]}"'
        tag_string_for_yaml = f'[{tag_string[2:]}]'

        self._metadata_html = f'{self._metadata_html}<meta name="tags" content={tag_string_for_html}>'
        self._metadata_yaml = f'{self._metadata_yaml}tags: {tag_string_for_yaml}\n'

    def __add_head_wrapper(self):
        self._metadata_html = f"<head>{self._metadata_html}</head>"
        self._metadata_yaml = f"---\n{self._metadata_yaml}---\n"

    @property
    def metadata_html(self):
        return self._metadata_html

    @property
    def metadata_yaml(self):
        return self._metadata_yaml

    @property
    def metadata_text(self):
        return self._metadata_text


class CheckListItem(ABC):
    def __init__(self, raw_item_htm):
        self._raw_item_html = raw_item_htm
        self._processed_item = str
        self._item_checked = False
        self._item_text = str
        self._check_list_level = 1
        self.__find_item_text()
        self.__find_status()
        self.__find_item_level()
        self.build_processed_item()

    @property
    def raw_item_html(self):
        return self._raw_item_html

    @property
    def processed_item(self):
        return self._processed_item

    @abstractmethod
    def build_processed_item(self):
        pass

    def __find_item_text(self):
        matches = re.findall('<input class=[^>]*syno-notestation-editor-checkbox[^>]*src=[^>]*type=[^>]*>([^<]*)',
                             self._raw_item_html)
        self._item_text = matches[0]

    def __find_status(self):
        matches = re.findall('syno-notestation-editor-checkbox-checked', self._raw_item_html)
        if matches:
            self._item_checked = True

    def __find_item_level(self):
        matches = re.findall('[0-9]{2}', self._raw_item_html)
        if matches:
            indent = int(matches[0])
            self._check_list_level = indent // 30


class GenerateMarkdownCheckListItem(CheckListItem):
    def build_processed_item(self):
        tabs = '\t' * self._check_list_level
        checked = ' '
        if self._item_checked:
            checked = 'x'

        self._processed_item = f"{tabs}- [{checked}] {self._item_text}"


class GenerateHTMLCheckListItem(CheckListItem):
    def build_processed_item(self):
        indent = self._check_list_level * 30
        checked = ''
        if self._item_checked:
            checked = 'checked'

        self._processed_item = f'<p style="padding-left: {indent}px;"><input type="checkbox" {checked}/>{self._item_text}</p> '


class ImageTag:
    def __init__(self, raw_tag, attachments):
        self._attachments = attachments
        self._raw_tag = raw_tag
        self._processed_tag = ''
        self._ref = ''
        self._width = ''
        self._relative_path = ''
        self.__set_ref_and_relative_path()
        self.__set_width()
        self._processed_tag = f"<img src={self._relative_path} {self._width}>"
        pass

    def __set_ref_and_relative_path(self):
        for attachment in self._attachments.values():
            if isinstance(attachment, ImageNSAttachment) and attachment.image_ref in self._raw_tag:
                self._ref = attachment.image_ref
                self._relative_path = str(attachment.path_relative_to_notebook)

    def __set_width(self):
        if 'width="' in self._raw_tag:
            width = re.findall('width="[0-9]*"', self._raw_tag)
            self._width = width[0]

    @property
    def processed_tag(self):
        return self._processed_tag

    @property
    def raw_tag(self):
        return self._raw_tag


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
            check_list_items = [GenerateHTMLCheckListItem(item) for item in raw_checklists_items]
        else:
            check_list_items = [GenerateMarkdownCheckListItem(item) for item in raw_checklists_items]

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

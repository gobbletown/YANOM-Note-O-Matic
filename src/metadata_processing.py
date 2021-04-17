import frontmatter
import logging
import inspect

from frontmatter import YAMLHandler, TOMLHandler, JSONHandler

from globals import APP_NAME
from bs4 import BeautifulSoup


def what_module_is_this():
    return __name__


def what_method_is_this():
    return inspect.currentframe().f_back.f_code.co_name


def what_class_is_this(obj):
    return obj.__class__.__name__


class MetaDataProcessor:
    def __init__(self, conversion_settings):
        self.logger = logging.getLogger(f'{APP_NAME}.{what_module_is_this()}.{what_class_is_this(self)}')
        self.logger.setLevel(logging.DEBUG)
        self._conversion_settings = conversion_settings
        self._split_tags = conversion_settings.split_tags
        self._spaces_in_tags = conversion_settings.split_tags
        self._metadata_schema = conversion_settings.metadata_schema
        self._metadata = {}
        self._tags = None

    def parse_html_metadata(self, html_metadata_source):
        soup = BeautifulSoup(html_metadata_source, 'html.parser')

        head = soup.find('head')
        if head is None:
            self.logger.info('No <head> section in html skipping meta data parsing')
            self._metadata = {}
            return

        for tag in head:
            if tag.name == 'meta':
                for key, value in tag.attrs.items():
                    if self._metadata_schema == [''] or key in self._metadata_schema:
                        self._metadata[key] = value

    def parse_dict_metadata(self, metadata_dict):
        for item in self._metadata_schema:
            if item in metadata_dict.keys():
                self._metadata[item] = metadata_dict[item]
            else:
                self.logger.info('Meta key {item} not found')

        self.format_tag_metadata_if_required()

    def parse_md_metadata(self, md_string):
        metadata, content = frontmatter.parse(md_string)
        if self._metadata_schema == ['']:
            self._metadata = {key: value for key, value in metadata.items()}
            return content

        self._metadata = {key: value for key, value in metadata.items() if key in self._metadata_schema}
        return content

    def format_tag_metadata_if_required(self):
        if 'tags' in self._metadata.keys():
            self.split_tags_if_required()
            self.remove_tag_spaces_if_required()

    def remove_tag_spaces_if_required(self):
        if self._spaces_in_tags:
            return

        self._metadata['tags'] = [tag.replace(' ', '-') for tag in self._metadata['tags']]

    def split_tags_if_required(self):
        if not self._split_tags:
            return

        set_tags = {tag for tag_split in self._metadata['tags'] for tag in tag_split.split('/')}
        self._metadata['tags'] = [tag for tag in set_tags]

    def add_metadata_md_to_content(self, content):

        if self._conversion_settings.front_matter_format == 'none':
            return content

        if len(self._metadata) == 0:  # if there is no meta data do not create an empty header
            return content

        if frontmatter.checks(content):
            self.logger.warning('Meta data front matter already exits, continuing to add a second front matter section')

        merged_content = frontmatter.Post(content, **self._metadata)

        if self._conversion_settings.front_matter_format == 'yaml':
            content = frontmatter.dumps(merged_content, handler=YAMLHandler())
            pass
        if self._conversion_settings.front_matter_format == 'toml':
            content = frontmatter.dumps(merged_content, handler=TOMLHandler())
        if self._conversion_settings.front_matter_format == 'json':
            content = frontmatter.dumps(merged_content, handler=JSONHandler())

        return content

    def add_metadata_html_to_content(self, content):
        if self._conversion_settings.markdown_conversion_input == 'markdown':
            return content

        if len(self._metadata) == 0:
            return content

        title_text = ''
        soup = BeautifulSoup(content, 'html.parser')

        head = soup.find('head')
        if head is None:
            self.logger.info("No <head> in html, skipping meta data insert")
            return content

        for key, value in self._metadata.items():
            if key.lower() == 'title':
                title_text = value
            meta_tag = soup.new_tag('meta')
            meta_tag.attrs[key] = value
            head.append(meta_tag)

        title = soup.find('title')
        if title is not None:
            if title_text:
                title.string = title_text

        return str(soup)

    @property
    def metadata(self):
        return self._metadata

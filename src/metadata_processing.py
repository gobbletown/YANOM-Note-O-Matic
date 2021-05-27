import logging

from bs4 import BeautifulSoup
import frontmatter
from frontmatter import YAMLHandler, TOMLHandler, JSONHandler

import config


def what_module_is_this():
    return __name__


class MetaDataProcessor:
    def __init__(self, conversion_settings):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._conversion_settings = conversion_settings
        self._split_tags = conversion_settings.split_tags
        self._spaces_in_tags = conversion_settings.split_tags
        self._tag_prefix = conversion_settings.tag_prefix
        self._metadata_schema = conversion_settings.metadata_schema
        self._metadata = {}
        self._tags = None

    def parse_html_metadata(self, html_metadata_source):
        self.logger.debug(f"Parsing HTML meta-data")
        soup = BeautifulSoup(html_metadata_source, 'html.parser')

        head = soup.find('head')
        if head is None:
            self.logger.debug('No <head> section in html skipping meta data parsing')
            self._metadata = {}
            return

        for tag in head:
            if tag.name == 'meta':
                for key, value in tag.attrs.items():
                    if self._metadata_schema == [''] or key in self._metadata_schema:
                        self._metadata[key] = value

        self.format_tag_metadata_if_required()

    def parse_dict_metadata(self, metadata_dict):
        self.logger.debug(f"Parsing a dictionary of meta-data")
        for item in self._metadata_schema:
            if item in metadata_dict.keys():
                self._metadata[item] = metadata_dict[item]
            else:
                self.logger.debug('Meta key {item} not found')

        self.format_tag_metadata_if_required()

    def parse_md_metadata(self, md_string):
        self.logger.debug(f"Parsing markdown front matter meta-data")
        metadata, content = frontmatter.parse(md_string)
        if self._metadata_schema == ['']:
            self._metadata = metadata
            return content

        self._metadata = {key: value for key, value in metadata.items() if key in self._metadata_schema}
        return content

    def format_tag_metadata_if_required(self):
        self.logger.debug(f"Formatting meta-data 'tags'")
        if 'tags' in self._metadata.keys() or 'tag' in self._metadata.keys():
            self.convert_tag_sting_to_tag_list()
            self.split_tags_if_required()
            self.remove_tag_spaces_if_required()

    def convert_tag_sting_to_tag_list(self):
        if 'tags' in self._metadata and len(self._metadata['tags']) > 0:
            if isinstance(self._metadata['tags'], str):
                self._metadata['tags'] = self.clean_tag_string(self._metadata['tags'])
        if 'tag' in self._metadata and len(self._metadata['tag']) > 0:
            if isinstance(self._metadata['tag'], str):
                self._metadata['tag'] = self.clean_tag_string(self._metadata['tag'])

    @staticmethod
    def clean_tag_string(tags):
        """Split a tag string into a list of tags and remove any spaces left from the comma separated list"""

        new_tags = []
        tag_list = tags.split(",")
        clean_tags = [tag.strip() for tag in tag_list]
        new_tags = new_tags + clean_tags
        return new_tags

    def remove_tag_spaces_if_required(self):
        if self._spaces_in_tags:
            return
        self.logger.debug(f"Removing spaces from 'tags'")
        if 'tags' in self._metadata:
            self._metadata['tags'] = [tag.replace(' ', '-') for tag in self._metadata['tags']]
        if 'tag' in self._metadata:
            self._metadata['tag'] = [tag.replace(' ', '-') for tag in self._metadata['tag']]

    def split_tags_if_required(self):
        if not self._split_tags:
            return
        self.logger.debug(f"Splitting 'tags'")
        if 'tags' in self._metadata:
            set_tags = {tag for tag_split in self._metadata['tags'] for tag in tag_split.split('/')}
            self._metadata['tags'] = [tag for tag in set_tags]
        if 'tag' in self._metadata:
            set_tags = {tag for tag_split in self._metadata['tag'] for tag in tag_split.split('/')}
            self._metadata['tag'] = [tag for tag in set_tags]

    def add_tag_prefix_if_required(self):
        if 'tags' in self._metadata:
            self._metadata['tags'] = [f'{self._tag_prefix}{tag}' for tag in self._metadata['tags']]
            return

        self._metadata['tag'] = [f'{self._tag_prefix}{tag}' for tag in self._metadata['tag']]

    def add_metadata_md_to_content(self, content):
        self.logger.debug(f"Add front matter meta-data to markdown page")
        if self._conversion_settings.front_matter_format == 'none':
            return content

        if len(self._metadata) == 0:  # if there is no meta data do not create an empty header
            return content

        if frontmatter.checks(content):
            self.logger.warning('Meta data front matter already exits, continuing to add a second front matter section')

        if self._conversion_settings.front_matter_format == 'text':
            content = self.add_text_metadata_to_content(content)
            return content

        merged_content = frontmatter.Post(content, **self._metadata)

        self._force_pandoc_markdown_to_yaml_front_matter()

        if self._conversion_settings.front_matter_format == 'yaml':
            content = frontmatter.dumps(merged_content, handler=YAMLHandler())
        if self._conversion_settings.front_matter_format == 'toml':
            content = frontmatter.dumps(merged_content, handler=TOMLHandler())
        if self._conversion_settings.front_matter_format == 'json':
            content = frontmatter.dumps(merged_content, handler=JSONHandler())

        return content

    def _force_pandoc_markdown_to_yaml_front_matter(self):
        if self._conversion_settings.export_format == 'pandoc_markdown':
            self._conversion_settings.front_matter_format = 'yaml'

    def add_text_metadata_to_content(self, content):
        self.logger.debug(f"Add plain text meta-data to page")

        if len(self._metadata) == 0:
            return content

        text_meta_data = ''
        for key, value in self._metadata.items():
            if key == 'tag' or key == 'tags':
                if value is None:  # empty tag metadata
                    continue
                value = self.add_tag_prefix(value)
                text_meta_data = f'{text_meta_data}{key}: '
                for item in value:
                    text_meta_data = f'{text_meta_data}{item}, '
                # trim off last space and comma
                text_meta_data = text_meta_data[:-2]
                continue

            text_meta_data = f'{text_meta_data}{key}: {value}\n'

        return f'{text_meta_data}\n{content}'

    def add_tag_prefix(self, tags):
        self.logger.debug(f"Add tag prefix")
        tags = [f'{self._tag_prefix}{tag}' for tag in tags]

        return tags

    def add_metadata_html_to_content(self, content):
        self.logger.debug(f"Add meta-data to html header")
        if len(self._metadata) == 0:
            return content

        title_text = ''
        soup = BeautifulSoup(content, 'html.parser')

        head = soup.find('head')
        if head is None:
            self.logger.debug("No <head> in html, skipping meta data insert")
            return content

        for key, value in self._metadata.items():
            if key.lower() == 'title':
                title_text = value
            meta_tag = soup.new_tag('meta')
            if isinstance(value, list):
                meta_tag.attrs[key] = ','.join(value)
            else:
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

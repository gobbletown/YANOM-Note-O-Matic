import time
from abc import ABC, abstractmethod


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
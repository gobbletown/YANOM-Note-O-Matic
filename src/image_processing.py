import re

from sn_attachment import ImageNSAttachment


class ImageTag:
    def __init__(self, raw_tag, attachments):
        self._attachments = attachments
        self._raw_tag = raw_tag
        self._processed_tag = ''
        self._ref = ''
        self._width = None
        self._relative_path = ''
        self._set_ref_and_relative_path()
        self._set_width()
        self._create_new_tag()

    def _set_ref_and_relative_path(self):
        for attachment in self._attachments.values():
            if isinstance(attachment, ImageNSAttachment) and attachment.image_ref in self._raw_tag:
                self._ref = attachment.image_ref
                self._relative_path = str(attachment.path_relative_to_notebook)

    def _set_width(self):
        if 'width="' in self._raw_tag:
            width = re.findall(r'width="([0-9]*)[^"]*"', self._raw_tag)
            self._width = width[0]

    def _create_new_tag(self):
        if self._width is None:
            self._processed_tag = f'<img src="{self._relative_path}">'
            return

        self._processed_tag = f'<img src="{self._relative_path}" width="{self._width}">'

    @property
    def processed_tag(self):
        return self._processed_tag

    @property
    def raw_tag(self):
        return self._raw_tag


class ObsidianImageTagFormatter:
    def __init__(self, content, generate_format):
        self._processed_content = content
        self._generate_format = generate_format
        if generate_format == 'obsidian':
            self._gfm_auto_links_to_obsidian_markdown()
        if generate_format == 'gfm':
            self._obsidian_markdown_links_to_gfm_auto_links()

    @property
    def processed_content(self):
        return self._processed_content

    def _gfm_auto_links_to_obsidian_markdown(self):
        images = self._find_gfm_auto_links_image_links()

        if not images:
            return

        for image in images:
            width = re.search('width="([0-9]*)"', image).group(1)

            file_path = re.match('^<img src=\"(.*?)\"', image).group(1)

            new_image_tag = f'![|{width}]({file_path})'

            self._processed_content = self._processed_content.replace(image, new_image_tag)

    def _find_gfm_auto_links_image_links(self):
        return re.findall('<img src=[^>]*width="[0-9]*"[^>]*>', self._processed_content)

    def _obsidian_markdown_links_to_gfm_auto_links(self):
        images = self._find_obsidian_image_links()

        if not images:
            return

        for image in images:
            width = re.search(r'!\[\w*\|(\d*)]\(.*?\)', image).group(1)

            file_path = re.match(r'!\[\w*\|\d*]\((.*?)\)', image).group(1)

            new_image_tag = f'<img src="{file_path}" width="{width}">'

            self._processed_content = self._processed_content.replace(image, new_image_tag)

    def _find_obsidian_image_links(self):
        return re.findall(r'!\[\w*\|\d*]\(.*?\)', self._processed_content)

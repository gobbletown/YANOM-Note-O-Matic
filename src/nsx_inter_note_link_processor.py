import logging
import re

import config


def what_module_is_this():
    return __name__


class NSXInterNoteLinkProcessor:
    """
    Attempt to create valid links to other notes pages using the link title text.

    Replace html '<a href=' tag links with new links.  Links to new file names are created if the link title matches
    a page name.  If more than one page name matches then link to all matches.  If a link has been renamed and no
    longer matches a page, search links that have already been linked to pages and if the href link value matches
    use those links.

    The links are not guaranteed to be valid/correct but this is currently the best guess for links to other note pages.

    """

    def __init__(self):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._raw_note_links = []
        self._replacement_links = []
        self._renamed_links_not_corrected = {}
        self._unmatched_links_msg = ''

    class IntraPageLink:
        """
        Hold details of 'a' tag href link and, generate a replacement 'a' tag href link to a valid file name
        """

        def __init__(self, raw_link, source_note):
            self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
            self.logger.setLevel(config.logger_level)
            self._raw_link = raw_link
            self._text = re.findall(r'<a href="notestation://[^>]*>([^<]*)</a>', raw_link)[0]
            self._link_id = re.findall(r'<a href="notestation://remote/self/(.*)">[^<]*</a>', raw_link)[0]
            self._replacement_text: list[str] = []
            self._source_note_page = source_note
            self._target_notes = []

        def generate_new_links(self):
            self.logger.debug("Creating inter note links")
            for target_note in self._target_notes:
                if self._source_note_page.parent_notebook == target_note.parent_notebook:
                    replacement_text = f'<a href="{target_note.file_name}">{self._text}</a>'
                else:
                    replacement_text = f'<a href="../{target_note.notebook_folder_name}/{target_note.file_name}">{self._text}</a>'

                self._replacement_text.append(replacement_text)

        @property
        def text(self):
            return self._text

        @property
        def target_notes(self):
            return self._target_notes

        @property
        def replacement_text(self):
            return self._replacement_text

        def append_to_target_notes(self, target_notes: list):
            self._target_notes = self._target_notes + target_notes

        @property
        def link_id(self):
            return self._link_id

        @property
        def raw_link(self):
            return self._raw_link

        @property
        def source_note_page(self):
            return self._source_note_page

    def make_list_of_links(self, all_note_pages):
        new_replacement_links = []
        for note in all_note_pages:
            new_raw_note_links = re.findall(r'<a href="notestation://[^>]*>[^>]*>', note.raw_content)
            self._raw_note_links = self._raw_note_links + new_raw_note_links

            new_replacement_links = new_replacement_links + [self.IntraPageLink(raw_link, note)
                                                             for raw_link in new_raw_note_links]

        self._replacement_links = self._replacement_links + new_replacement_links

    def match_link_title_to_notes(self, all_note_pages):
        for intra_page_link_obj in self._replacement_links:
            for note in all_note_pages:
                if intra_page_link_obj.text == note.original_title:
                    intra_page_link_obj.append_to_target_notes([note])

    def match_renamed_links_using_link_ref_id(self):
        links_not_yet_matched = [inter_note_link
                                 for inter_note_link in self._replacement_links
                                 if not inter_note_link.target_notes
                                 ]

        matched_links = [inter_note_link
                         for inter_note_link in self._replacement_links
                         if inter_note_link.target_notes
                         ]

        for unmatched_link in links_not_yet_matched:
            for matched_link in matched_links:
                if unmatched_link.link_id == matched_link.link_id and unmatched_link is not matched_link:
                    unmatched_link.append_to_target_notes(matched_link.target_notes)

        self._renamed_links_not_corrected = [inter_note_link
                                             for inter_note_link in self._replacement_links
                                             if not inter_note_link.target_notes
                                             ]

        self._replacement_links = list(set(self._replacement_links) - set(self._renamed_links_not_corrected))

        if self._renamed_links_not_corrected:
            self._log_link_unmatched_links()

    def _log_link_unmatched_links(self):
        self._generate_unmatched_links_message()
        unmatched_links_msg = 'The following links could not be corrected.\n'
        for link in self._renamed_links_not_corrected:
            unmatched_links_msg = f'{unmatched_links_msg}On page {link.source_note_page.title} - {link.raw_link}\n'

        self.logger.info(self._unmatched_links_msg)

    def _generate_unmatched_links_message(self):
        unmatched_links_msg = 'The following link(s) could not be corrected.\n'
        for link in self._renamed_links_not_corrected:
            unmatched_links_msg = f'{unmatched_links_msg}On page - {link.source_note_page.title} - {link.raw_link}\n'

        self._unmatched_links_msg = unmatched_links_msg

    def update_content(self, content):
        self.logger.debug("Adding inter note links to page")
        raw_note_links = re.findall(r'<a href="notestation://[^>]*>[^>]*>', content)

        if not raw_note_links:
            return content

        replacement_links = {replacement_link.raw_link: replacement_link for replacement_link in
                             self._replacement_links}

        for raw_link in raw_note_links:
            if raw_link in replacement_links:
                replacement_links[raw_link].generate_new_links()
                content = content.replace(raw_link,
                                    self.generate_html_code_for_new_links(replacement_links[raw_link].replacement_text))

        return content

    @staticmethod
    def generate_html_code_for_new_links(replacement_links):
        if len(replacement_links) == 1:
            return f'{replacement_links[0]}'

        html_code = ''
        for replacement_link in replacement_links:
            html_code = f'{html_code}{replacement_link}<br>'
        return html_code

    @property
    def renamed_links_not_corrected(self):
        return self._renamed_links_not_corrected

    @property
    def unmatched_links_msg(self):
        return self._unmatched_links_msg

    @property
    def replacement_links(self):
        return self._replacement_links

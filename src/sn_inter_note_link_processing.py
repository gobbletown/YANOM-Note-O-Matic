import logging
import re

import config


def what_module_is_this():
    return __name__


class SNLinksToOtherNotes:
    """
    Attempt to create valid links to other notes pages using the link title text.

    Replace html '<a href=' tag links with new links.  Links to new file names are created if the link title matches
    a page name.  If more than one page name matches then link to all matches.  If a link has been renamed and no
    longer matches a page, search links that have already been linked to pages and if the href link value matches
    use those links.

    The links are not guaranteed to be valid/correct but this is currently the best guess for links to other note pages.

    """

    def __init__(self, note, content, all_note_pages):
        self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
        self.logger.setLevel(config.logger_level)
        self._note_page = note
        self._content = content
        self._raw_note_links = []
        self._links_on_this_page = {}
        self._all_note_pages = all_note_pages
        self._replacement_links = {}

    class IntraPageLink:
        """
        Hold details of 'a' tag href link and, generate a replacement 'a' tag href link to a valid file name
        """

        def __init__(self, raw_link, text_from_link, note, href_note):
            self.logger = logging.getLogger(f'{config.APP_NAME}.{what_module_is_this()}.{self.__class__.__name__}')
            self.logger.setLevel(config.logger_level)
            self._raw_link = raw_link
            self._text_from_link = text_from_link
            self._href_text = ''
            self._href_link_value = re.findall('<a href=\"(.*)\"', raw_link)[0]
            self._new_link = ''
            self._note_page = note
            self._href_note = href_note

            self._generate_new_link()

        def _generate_new_link(self):
            self.logger.debug("Creating inter note links")
            self._new_link = f'<a href="{self._href_note.file_name}">{self._text_from_link}</a>'
            if self._note_page.parent_notebook != self._href_note.parent_notebook:
                self._new_link = f'<a href="../{self._href_note.notebook_folder_name}/{self._href_note.file_name}">{self._text_from_link}</a>'

        @property
        def new_link(self):
            return self._new_link

        @property
        def href_link_value(self):
            return self._href_link_value

        @property
        def href_note(self):
            return self._href_note

    def _generate_dict_of_links(self):
        """
        Generate a dictionary where the keys are text strings displayed on a page and the values are the raw
        and unusable href links, because they do not link to anything in an nsx export file
        :return:
        """
        self._raw_note_links = re.findall('<a href="notestation://[^>]*>[^>]*>', self._content)

        link_text = []
        # link_text values are the displayed text for each link this is the only way we have of
        # finding which note page each link should link to
        for raw_link in self._raw_note_links:
            text_from_link = re.findall('<a href="notestation://[^>]*>([^<]*)</a>', raw_link)
            link_text.append(text_from_link[0])

        self._links_on_this_page = dict(zip(self._raw_note_links, link_text))

    def process_inter_note_links(self):
        self._generate_dict_of_links()
        if self._links_on_this_page:
            self._match_link_title_to_a_note()
            self._find_potential_match_for_renamed_links()
            self._update_content()

    def _match_link_title_to_a_note(self):
        """
        For each of the link on this note page use the text value find all the occurrences of note pages of the same name.
        Creating a list containing IntraPageLink objects for each one.
        The IntraPage Link object handles the creation of a new valid link.

        """
        for raw_link, text_from_link in self._links_on_this_page.items():
            replacement_links = [self.IntraPageLink(raw_link, text_from_link, self._note_page, target_note.note)
                                 for target_note in self._all_note_pages
                                 if text_from_link == target_note.title]
            if replacement_links:
                self._replacement_links[raw_link] = replacement_links

    def _find_potential_match_for_renamed_links(self):
        """
        Match renamed links to links already identified

        A renamed link will not have a display text string that matches a note name.  However the unusable href
        will not be changed when the text was edited.  If that href link has already been matched to a note page
        because that link was not edited then we can use the bad href to match the link to the real note page.

        """
        for raw_link in self._raw_note_links:
            new_replacement_links = {}
            if raw_link not in self._replacement_links.keys():  # then it is a renamed link
                self.logger.debug(f"Attempting to create links for renamed links")
                # search already found replacement links for this links href value and if found give it a new link
                for replacement_links in self._replacement_links.values():
                    if re.findall('<a href=\"(.*)\"', raw_link)[0] == replacement_links[0].href_link_value:
                        new_replacement_links[raw_link] = [self.IntraPageLink(raw_link, re.findall('<a href="notestation://[^>]*>([^<]*)</a>', raw_link)[0] , self._note_page,
                                                                              replacement_links[0].href_note)]

            # now merge the renamed link replacement link dict into the main replacement_links dict
            self._replacement_links = {**self._replacement_links, **new_replacement_links}

    def _update_content(self):
        self.logger.debug("Adding inter note links to page")
        for raw_link, replacement_links in self._replacement_links.items():
            self._content = self._content.replace(raw_link, self._generate_html_code_for_new_links(replacement_links))

    @staticmethod
    def _generate_html_code_for_new_links(links):
        if len(links) == 1:
            return f'{links[0].new_link}'

        html_code = ''
        for link in links:
            html_code = f'{html_code}{link.new_link}<br>'
        return html_code

    @property
    def content(self):
        return self._content

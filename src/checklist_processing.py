from bs4 import BeautifulSoup
import re
from abc import ABC, abstractmethod


class ChecklistItem:
    def __init__(self):
        self._text = ''
        self._checked = False
        self._indent = 0
        self._placeholder_text = ''
        self._markdown_item_text = ''
        self.__create_placeholder_text()

    def __create_placeholder_text(self):
        self._placeholder_text = f'checklist-placeholder-id-{str(id(self))}'

    def generate_markdown_item_text(self):
        tabs = '\t' * self._indent
        checked = ' '
        if self._checked:
            checked = 'x'

        self._markdown_item_text = f"{tabs}- [{checked}] {self._text}"

    @property
    def placeholder_text(self):
        return self._placeholder_text

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value

    @property
    def indent(self):
        return self._indent

    @indent.setter
    def indent(self, value):
        self._indent = int(value)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def markdown_item_text(self):
        return self._markdown_item_text

    @property
    def clean_html(self):
        return self._clean_html


class ChecklistProcessor(ABC):
    def __init__(self, html):
        self._raw_html = html
        self._processed_html = ''
        self._list_of_checklist_items = []
        self._soup = BeautifulSoup(self._raw_html, 'html.parser')
        self.__checklist_pre_processing()

    @property
    def processed_html(self):
        return self._processed_html

    @property
    def list_of_checklist_items(self):
        return self._list_of_checklist_items

    def __checklist_pre_processing(self):

        checklists = self.find_all_checklist_items()

        for tag in checklists:
            this_checklist_item = ChecklistItem()

            this_checklist_item.checked = self.find_checked_status(tag)

            this_checklist_item.text = self.find_checklist_item_text(tag)

            this_checklist_item.indent = self.find_indent(tag)

            self.replace_item_html_with_new_text(tag, this_checklist_item)

            self._list_of_checklist_items.append(this_checklist_item)

        self.__calculate_indents_and_generate_cleaned_checklist_items()

        self._processed_html = str(self._soup)

    def __calculate_indents_and_generate_cleaned_checklist_items(self):
        set_of_indents = {item.indent for item in self._list_of_checklist_items}

        list_of_indents = sorted(set_of_indents)

        indent_level_lookup = {list_of_indents[level]: level for level in range(0, len(list_of_indents))}

        for item in self._list_of_checklist_items:
            item.indent = indent_level_lookup[item.indent]
            item.generate_markdown_item_text()

    def add_checklist_items_to(self, markdown_text):
        for item in self._list_of_checklist_items:
            search_for = rf'\ *{item.placeholder_text}'   # removing leading spaces as would stop markdown working
            replace_with = f'{item.markdown_item_text}\n'
            markdown_text = re.sub(search_for, replace_with, markdown_text)
        return markdown_text

    @abstractmethod
    def find_all_checklist_items(self):
        pass

    @staticmethod
    @abstractmethod
    def find_checked_status(tag):
        pass

    @staticmethod
    def find_checklist_item_text(tag):
        return tag.parent.text

    @staticmethod
    def find_indent(tag):
        if 'style' in tag.parent.attrs:
            style = tag.parent.attrs['style']
            match = re.findall(r'(?:padding|margin)-left[^\d]*(\d+)', style)
            if match:
                return int(match[0])
        return 0

    @staticmethod
    def replace_item_html_with_new_text(tag, this_checklist_item):
        tag.parent.replace_with(f'{this_checklist_item.placeholder_text}')


class HTMLInputMDOutputChecklistProcessor(ChecklistProcessor):

    def find_all_checklist_items(self):
        return self._soup.select('input[type="checkbox"]')

    @staticmethod
    def find_checked_status(tag):
        return 'checked' in tag.attrs


class NSXInputMDOutputChecklistProcessor(ChecklistProcessor):

    def find_all_checklist_items(self):
        checked = self._soup.select(
            'input[class="syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked"]')
        unchecked = self._soup.select('input[class="syno-notestation-editor-checkbox"]')

        return checked + unchecked

    @staticmethod
    def find_checked_status(tag):
        return 'syno-notestation-editor-checkbox-checked' in tag.attrs['class']


class NSXInputHTMLOutputChecklistProcessor(NSXInputMDOutputChecklistProcessor):
    def replace_item_html_with_new_text(self, tag, this_checklist_item):
        del tag['class']
        del tag['src']
        del tag['type']
        if this_checklist_item.checked:
            tag['checked'] = ''
        tag['type'] = 'checkbox'


if __name__ == '__main__':
    pass

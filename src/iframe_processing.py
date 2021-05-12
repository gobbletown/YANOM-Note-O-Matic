"""Locate, remove, and reinsert HTML iframes

Pandoc does not handle iframes when converting from HTML into Markdown.
This module allows iframes to be retained when converting HTML-Markdown, the pre and post porocess functions
would be called before and aftger pandoc conversion

"""
from bs4 import BeautifulSoup
import re
from typing import Tuple


def pre_process_iframes_from_html(raw_content: str) -> Tuple[str, dict]:
    """Locate, and replace iframes with placeholder ID

    Parameters
    ----------
    raw_content : str
        A string of HTML code to be parsed for iframe tags.

    Returns
    -------
    processed_content: str
        The raw_content with iframe code replaced with a unique placeholder string
    iframes_dict: dict
        Dictionary where the key is the unique placeholder string, the value is the iframe beautiful soup tag object

    """
    soup = BeautifulSoup(raw_content, 'html.parser')

    iframes = soup.select('iframe')
    iframes_dict = {}
    for iframe in iframes:
        placeholder_text = f'iframe-placeholder-id-{str(id(iframe))}'
        iframes_dict[placeholder_text] = iframe
        iframe.replace_with(f'{placeholder_text}')

    processed_content = str(soup)

    return processed_content, iframes_dict


def post_process_iframes_to_markdown(content, iframes_dict) -> str:
    """Locate, and replace placeholder ID with iframe code

    Parameters
    ----------
    content : str
        A string of HTML code to be parsed for iframe tags.
    iframes_dict: dict
        Dictionary where the key is the unique placeholder string, the value is the iframe beautiful soup tag object

    Returns
    -------
    content: str
        The raw_content with iframe code replacing the unique placeholder string.

    """
    for key, value in iframes_dict.items():
        search_for = rf'\ *{key}'  # including leading spaces to leave a blank line
        replace_with = f'\n{value}\n' # new line either side of html code is required for some readers
        content = re.sub(search_for, replace_with, content)

    return content

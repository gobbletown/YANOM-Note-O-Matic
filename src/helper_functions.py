from pathlib import Path
import random
import re
import string
import sys
from typing import Tuple
import unicodedata


def find_working_directory(is_frozen=getattr(sys, 'frozen', False)) -> Tuple[Path, str]:
    """
    This function helps fetch the current working directory when a program may be run in a frozen pyinstaller bundle or
    in a python environment.

    Returns
    -------
    current_directory_path
        Path object of the absolute path for the current working directory
    message
        Str that describes if the program is run as a bundle or in python and the current working directory path
    """
    if is_frozen:
        # we are running in a bundle
        current_directory_path = Path(sys.executable).parent.absolute()
        message = f"Running in a application bundle, current path is {current_directory_path}"
    else:
        # we are running in a normal Python environment
        current_directory_path = Path(__file__).parent.absolute()
        message = f"Running in a python environment, current path is {current_directory_path}"

    return current_directory_path, message


def generate_clean_path(value, allow_unicode=False):
    """
    This function is adapted from https://github.com/django/django/blob/master/django/utils/text.py
    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    value: str of path or a path part - a folder name, or a file name
    returns: Path object
    """
    value = str(value)
    parts = [Path(value).stem, Path(value).suffix]
    for i in range(len(parts)):
        if not len(parts[i]):
            continue

        if allow_unicode:
            parts[i] = unicodedata.normalize('NFKC', parts[i])
        else:
            parts[i] = unicodedata.normalize('NFKD', parts[i]).encode('ascii', 'ignore').decode('ascii')
        parts[i] = re.sub(r'[^\w\s-]', '', parts[i].lower())

        parts[i] = re.sub(r'[-\s]+', '-', parts[i]).strip('-_')

    if len(parts[1]):
        return Path(f"{parts[0]}.{parts[1]}")

    return Path(parts[0])


def find_valid_full_file_path(path_to_file: Path) -> Path:
    """
    Test if file exists and add an incrementing number to the file name until a valid file name is found.

    Parameters
    ----------
    path_to_file:
        PAth object of the absolute path to a file

    Returns
    -------
    path_to_file
        Path object of the absolute path for the new incremented file name
    """
    n = 0
    path_to_folder = path_to_file.parent
    stem = path_to_file.stem
    while path_to_file.exists():
        n += 1
        path_to_file = Path(path_to_folder, f"{stem}-{n}{path_to_file.suffix}")

    return path_to_file


def add_random_string_to_file_name(path, length: int):
    """
    Add a random character sting to a file name.

    The path can be the file name or a path including the file name.
    For example '/something/file.txt' becomes '/something/file-kjgd.txt' if length is 4

    Parameters
    ----------
    path : string or pathlib.Path object
        filename or full path to file
    length : int
        length of random character strong to be added to end of file name.
    Returns
    -------
    Path:
        pathlib.Path object of the new path/filename
    """
    stem = Path(path).stem
    stem = f"{stem}-{_get_random_string(length)}"
    new_filename = f"{stem}{Path(path).suffix}"
    path = Path(Path(path).parent, new_filename)
    return path


def _get_random_string(length: int):
    "Return a string of length random characters.  If length is zero or negative value empty string is returned."
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def add_strong_between_tags(front_tag, rear_tag, old_html):
    """
    Add <strong> tags inside of the provided front and rear tag throughout the entire html content provided.

    If the tags provided are not found no replacement is made.  There is no validation of tag validity.

    Parameters
    ----------
    front_tag : str
        String representing the front tag to be replaced for example '<p>'.
    rear_tag : str
        String representing the rear tag to be replaced for example '<\p>'.
    old_html : str
        String containing the html content to be searched for tags that will be replaced.

    Returns
    -------
    str:
        html content with additional strong tags.

    """
    old_values = _find_tags(front_tag, rear_tag, old_html)
    new_values = [f'<strong>{item}</strong>' for item in old_values]
    return _update_html_with_changed_tags(front_tag, rear_tag, front_tag, rear_tag,
                                           old_html, old_values, new_values)


def change_html_tags(front_tag, rear_tag, new_front_tag, new_rear_tag, old_html):
    """
    Replace a given pair of tags with a new set of tags throughout the entire html content provided.

    If the tags provided are not found no replacement is made.  There is no validation of tag validity.

    Parameters
    ----------
    front_tag : str
        String representing the front tag to be replaced for example '<p>'.
    rear_tag : str
        String representing the rear tag to be replaced for example '<\p>'.
    new_front_tag : str
        String representing the new front tag to be replaced for example '<div>'.
    new_rear_tag : str
        String representing the rear tag to be replaced for example '<\div>'.
    old_html : str
        String containing the html content to be searched for tags that will be replaced.

    Returns
    -------
    str:
        html content with replaced tags.

    """
    values = _find_tags(front_tag, rear_tag, old_html)
    return _update_html_with_changed_tags(front_tag, rear_tag, new_front_tag, new_rear_tag,
                                           old_html, values)


def _update_html_with_changed_tags(front_tag, rear_tag, new_front_tag, new_rear_tag,
                                    html, old_values, new_values=None):
    if new_values is None:
        new_values = old_values
    for i in range(len(old_values)):
        html = html.replace(f'{front_tag}{old_values[i]}{rear_tag}',
                            f'{new_front_tag}{new_values[i]}{new_rear_tag}')
    return html


def _find_tags(front_tag, rear_tag, html):
    return re.findall(f'{front_tag}([^<]*){rear_tag}', html)


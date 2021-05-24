from pathlib import Path

import pytest

import helper_functions


def test_find_valid_full_file_path_rename_expected(tmp_path):
    folder_name = "my-folder"
    Path(tmp_path, folder_name, 'file_name.txt').mkdir(parents=True, exist_ok=False)
    Path(tmp_path, folder_name, 'file_name-1.txt').mkdir(parents=True, exist_ok=False)
    path_to_test = Path(tmp_path, folder_name, 'file_name.txt')
    full_path = helper_functions.find_valid_full_file_path(path_to_test)
    assert full_path == Path(tmp_path, folder_name, 'file_name-2.txt')


def test_find_valid_full_file_path_no_rename_expected(tmp_path):
    folder_name = "my-folder"
    path_to_test = Path(tmp_path, folder_name, 'file_name.txt')
    full_path = helper_functions.find_valid_full_file_path(path_to_test)
    assert full_path == Path(tmp_path, folder_name, 'file_name.txt')


@pytest.mark.parametrize(
    'length, expected_length_or_random_string', [
        (0, 0),
        (-1, 0),
        (1, 1),
        (4, 4),
    ]
)
def test_add_random_string_to_file_name(length, expected_length_or_random_string):
    old_path = 'dir/file.txt'
    new_path = helper_functions.add_random_string_to_file_name(old_path, length)

    assert len(new_path.name) == len(Path(old_path).name) + expected_length_or_random_string + 1


def test_add_strong_between_tags():
    result = helper_functions.add_strong_between_tags('<p>', '</p>', '<p>hello world</p>')

    assert result == '<p><strong>hello world</strong></p>'


def test_add_strong_between_tags_invalid_tags():
    result = helper_functions.add_strong_between_tags('<x>', '</x>', '<p>hello world</p>')

    assert result == '<p>hello world</p>'


def test_change_html_tags():
    result = helper_functions.change_html_tags('<p>', '</p>', '<div>', '</div>', '<div><p>hello world</p></div>')

    assert result == '<div><div>hello world</div></div>'


def test_change_html_tags_invalid_old_tags():
    result = helper_functions.change_html_tags('<g>', '</g>', '<div>', '</div>', '<div><p>hello world</p></div>')

    assert result == '<div><p>hello world</p></div>'


def test_find_working_directory_when_frozen():
    current_dir, message = helper_functions.find_working_directory(True)

    assert 'Running in a application bundle' in message


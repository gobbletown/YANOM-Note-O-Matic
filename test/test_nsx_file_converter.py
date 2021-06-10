from mock import patch
from pathlib import Path
import pytest

import config
import conversion_settings
import nsx_file_converter
import sn_note_page
import sn_notebook


@pytest.fixture
def all_notes_dict(all_notes):
    return {id(note): note for note in all_notes}


def test_build_dictionary_of_inter_note_links(conv_setting, all_notes_dict, ):
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')
    nsx_fc._note_pages = all_notes_dict
    nsx_fc.build_dictionary_of_inter_note_links()

    assert len(nsx_fc._inter_note_link_processor.replacement_links) == 9
    assert len(nsx_fc._inter_note_link_processor.renamed_links_not_corrected) == 1


def test_generate_note_page_filename_and_path(nsx, conv_setting):
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    # Note with no links
    note_page_1_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539,
                        'attachment': {}, 'content': 'content', 'tag': [1]}
    note_page_1 = sn_note_page.NotePage(nsx, 1, note_page_1_json)
    note_page_1.notebook_folder_name = 'note_book1'
    note_page_1._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div>"""

    nsx_fc._note_pages = {id(note_page_1): note_page_1}
    nsx_fc.generate_note_page_filename_and_path()

    for note in nsx_fc._note_pages.values():
        assert note.file_name == 'page-1-title.md'


def test_fetch_json_data(conv_setting):
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    with patch('zip_file_reader.read_json_data', spec=True, return_value='fake_json') as mock_read_json_data:
        result = nsx_fc.fetch_json_data('data_id')

        assert result == 'fake_json'


def test_fetch_attachment_file(conv_setting):
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    with patch('zip_file_reader.read_binary_file', spec=True, return_value='fake_binary') as mock_read_binary_file:
        result = nsx_fc.fetch_attachment_file('data_id')

        assert result == 'fake_binary'


def test_add_notebooks(conv_setting):
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    nsx_fc._notebook_ids = ['1234', 'abcd']
    with patch('zip_file_reader.read_json_data', spec=True, return_value={'title': "notebook"}) as mock_read_json_data:
        nsx_fc.add_notebooks()

    assert nsx_fc.note_book_count == 2


@pytest.mark.parametrize(
    'json, expected', [
        ({'title': 'notebook'}, 'notebook'),
        ({'title': ''}, 'My Notebook')
    ]
)
def test_fetch_notebook_title(conv_setting, json, expected):
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    with patch('zip_file_reader.read_json_data', spec=True, return_value=json) as mock_read_json_data:
        result = nsx_fc.fetch_notebook_title('1234')

    assert result == expected


def test_add_recycle_bin_notebook(conv_setting, caplog):
    config.set_logger_level("DEBUG")
    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    nsx_fc.add_recycle_bin_notebook()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'DEBUG'

    assert len(nsx_fc._notebooks) == 1
    assert 'recycle-bin' in nsx_fc._notebooks.keys()


def test_create_export_folder_if_not_exist(conv_setting, caplog, tmp_path):
    config.set_logger_level("DEBUG")
    Path(tmp_path, config.DATA_DIR).mkdir()

    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    nsx_fc.conversion_settings.working_directory = tmp_path
    nsx_fc.conversion_settings.export_folder_name = 'notes'

    nsx_fc.create_export_folder_if_not_exist()

    assert Path(tmp_path, config.DATA_DIR, 'notes').exists()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'DEBUG'


def test_create_folders(conv_setting, caplog, tmp_path, nsx):
    config.set_logger_level("DEBUG")

    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    test_notebook = sn_notebook.Notebook(nsx, '1234', 'notebook title')
    nsx_fc._notebooks = {'1234': test_notebook}

    with patch('sn_notebook.Notebook.create_folders', spec=True) as mock_create_folders:
        nsx_fc.create_folders()

        mock_create_folders.assert_called_once()
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'DEBUG'


@pytest.mark.parametrize(
    'silent_mode, expected', [
        (True, ''),
        (False, 'Finding note pages')
    ]
)
def test_add_note_pages(conv_setting, caplog, silent_mode, expected):
    config.set_logger_level("DEBUG")
    config.set_silent(silent_mode)

    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')

    nsx_fc._note_page_ids = ['1234']

    with patch('zip_file_reader.read_json_data', spec=True, return_value={'title': 'note title', 'ctime': 1620808218, 'mtime': 1620808218, 'parent_id': '1234'}) as mock_read_json_data:
        caplog.clear()
        nsx_fc.add_note_pages()

    assert nsx_fc.note_page_count == 1

    assert nsx_fc.note_pages['1234'].title == 'note title'

    assert caplog.records[0].message == 'Creating note page objects'


@pytest.fixture
def note_pages(all_notes):
    return {id(note): note for note in all_notes}


@pytest.fixture
def notebooks(nsx):
    test_notebook1 = sn_notebook.Notebook(nsx, 'note_book1', 'notebook 1')
    test_notebook2 = sn_notebook.Notebook(nsx, 'recycle-bin', 'recycle bin')
    return {'note_book1': test_notebook1, 'recycle-bin': test_notebook2}


def test_add_note_pages_to_notebooks(conv_setting, caplog, nsx, note_pages, notebooks):
    config.set_logger_level("INFO")

    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')
    nsx_fc._notebooks = notebooks
    nsx_fc._note_pages = note_pages

    caplog.clear()
    nsx_fc.add_note_pages_to_notebooks()

    assert len(nsx_fc.notebooks['note_book1'].note_pages) == 6
    assert len(nsx_fc.notebooks['recycle-bin'].note_pages) == 5

    assert "Add note pages to notebooks" in caplog.records[0].message


def test_create_attachments(conv_setting, caplog, note_pages):
    config.set_logger_level("DEBUG")

    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')
    nsx_fc._note_pages = note_pages
    caplog.clear()
    nsx_fc.create_attachments()

    assert nsx_fc.image_count == 1
    assert nsx_fc.attachment_count == 3

    assert len(caplog.records) == 1
    assert "Creating attachment objects" in caplog.records[0].message


def test_process_notebooks(conv_setting, caplog, notebooks):
    config.set_logger_level("DEBUG")

    nsx_fc = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')
    nsx_fc._notebooks = notebooks

    with patch('sn_notebook.Notebook.process_notebook_pages', spec=True) as mock_process_notebook_pages:
        nsx_fc.process_notebooks()

        mock_process_notebook_pages.assert_called()

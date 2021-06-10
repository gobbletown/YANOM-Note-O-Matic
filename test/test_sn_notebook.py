from mock import patch
from pathlib import Path
import pytest

import config
import sn_note_page
import sn_notebook


def test_create_notebook_folder_folder_does_not_already_exist(tmp_path, nsx, caplog):
    config.set_logger_level("DEBUG")
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'abcd', notebook_title)

    notebook.conversion_settings.export_folder_name = 'export-folder'
    notebook.folder_name = 'notebook1'

    Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name).mkdir(parents=True, exist_ok=True)

    notebook.create_notebook_folder()

    assert Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name, notebook.folder_name).exists()

    assert notebook.folder_name == 'notebook1'
    assert notebook.full_path_to_notebook == Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name, notebook.folder_name)

    assert len(caplog.records) == 1
    assert caplog.records[0].message == f'Creating notebook folder for {notebook_title}'

def test_create_notebook_folder_folder_already_exist(tmp_path, nsx, caplog):
    config.set_logger_level("DEBUG")
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'abcd', notebook_title)

    notebook.conversion_settings.export_folder_name = 'export-folder'
    notebook.folder_name = 'notebook1'

    Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name, notebook.folder_name).mkdir(parents=True, exist_ok=True)
    expected_folder_name = 'notebook1-1'

    notebook.create_notebook_folder()

    assert Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name,
                expected_folder_name).exists()

    assert notebook.folder_name == expected_folder_name
    assert notebook.full_path_to_notebook == Path(tmp_path, config.DATA_DIR,
                                                  notebook.conversion_settings.export_folder_name, expected_folder_name)

    assert len(caplog.records) == 1
    assert caplog.records[0].message == f'Creating notebook folder for {notebook_title}'


def test_create_attachment_folder(tmp_path, nsx, caplog):
    config.set_logger_level("DEBUG")
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'abcd', notebook_title)
    notebook.full_path_to_notebook = Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name, 'notebook1')
    notebook.full_path_to_notebook.mkdir(parents=True, exist_ok=True)
    notebook.conversion_settings.attachment_folder_name = 'attachments'

    notebook.create_attachment_folder()

    assert Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name, 'notebook1', 'attachments').exists()

    assert len(caplog.records) == 1
    assert caplog.records[0].message == f'Creating attachment folder'


def test_create_folders(tmp_path, nsx, caplog):
    config.set_logger_level("DEBUG")
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'abcd', notebook_title)
    notebook.conversion_settings.attachment_folder_name = 'attachments'
    notebook.conversion_settings.export_folder_name = 'export-folder'
    notebook.folder_name = 'notebook1'

    Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name).mkdir(parents=True, exist_ok=True)

    notebook.create_folders()

    assert Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name,
                'notebook1').exists()
    assert Path(tmp_path, config.DATA_DIR, notebook.conversion_settings.export_folder_name, 'notebook1',
                'attachments').exists()

    assert len(caplog.records) == 2
    assert caplog.records[1].message == f'Creating attachment folder'
    assert caplog.records[0].message == f'Creating notebook folder for {notebook_title}'


def test_pair_up_note_pages_and_notebooks_note_title_does_not_already_exist(nsx):
    note_jason = {'parent_id': 'note_book2', 'title': 'Page 8 title',
                        'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [9]}
    note_page = sn_note_page.NotePage(nsx, '1234', note_jason)
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'notebook_id_abcd', notebook_title)
    notebook.folder_name = 'notebook_folder'

    notebook.note_titles = ['abcd']

    notebook.pair_up_note_pages_and_notebooks(note_page)

    assert note_page.notebook_folder_name == Path('notebook_folder')
    assert note_page.parent_notebook == 'notebook_id_abcd'

    assert note_page.title in notebook.note_titles
    assert note_page in notebook.note_pages


def test_pair_up_note_pages_and_notebooks_note_title_already_exists(nsx):
    note_jason = {'parent_id': 'note_book2', 'title': 'Page 8 title',
                        'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [9]}
    note_page = sn_note_page.NotePage(nsx, '1234', note_jason)
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'notebook_id_abcd', notebook_title)
    notebook.folder_name = 'notebook_folder'

    notebook.note_titles = ['abcd', 'Page 8 title', 'Page 8 title-1']

    notebook.pair_up_note_pages_and_notebooks(note_page)

    assert note_page.notebook_folder_name == Path('notebook_folder')
    assert note_page.parent_notebook == 'notebook_id_abcd'

    assert note_page.title == 'Page 8 title-2'
    assert note_page.title in notebook.note_titles
    assert note_page in notebook.note_pages


@pytest.mark.parametrize(
    'silent_mode, expected', [
        (True, ''),
        (False, "Processing 'notebook1' Notebook")
    ]
)
def test_process_notebook_pages(all_notes, tmp_path, nsx, silent_mode, expected, capsys, caplog):
    config.set_silent(silent_mode)
    notebook_title = 'notebook1'
    notebook = sn_notebook.Notebook(nsx, 'notebook_id_abcd', notebook_title)
    notebook.folder_name = 'notebook_folder'
    notebook.note_pages = all_notes

    with patch('sn_note_page.NotePage.process_note', spec=True) as mock_process_note:
        notebook.process_notebook_pages()

    mock_process_note.assert_called()

    assert caplog.records[0].message == f"Processing note book {notebook.title} - {notebook.notebook_id}"

    captured = capsys.readouterr()
    assert expected in captured.out



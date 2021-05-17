from pathlib import Path
import pytest

import config
import sn_note_writer
from conversion_settings import ManualConversionSettings


@pytest.mark.parametrize(
    'title, export_format, expected', [
        ('My Note', 'html', 'My Note.html'),
        ('My Note','gfm', 'My Note.md'),
    ]
)
def test_append_file_extension(title, export_format, expected):
    result = sn_note_writer.__append_file_extension(title, export_format)
    assert result == expected


def test_clean_filename():
    dirty_filename = 'My Note.html'
    result = sn_note_writer.__clean_filename(dirty_filename)
    assert result == Path('my-note.html')


def test_generate_valid_output_path_no_rename_expected():
    conversion_settings = ManualConversionSettings()
    conversion_settings.working_directory = Path('/test/path')
    conversion_settings.export_folder_name = 'notes'
    clean_filename = 'my-note.md'
    folder_name = "my-notebook"
    full_path = sn_note_writer.__generate_valid_output_path(conversion_settings, folder_name, clean_filename)
    assert full_path == Path(conversion_settings.working_directory, config.DATA_DIR, conversion_settings.export_folder_name, folder_name, clean_filename)


def test_generate_valid_output_path_rename_expected(tmp_path):
    conversion_settings = ManualConversionSettings()
    conversion_settings.working_directory = tmp_path
    conversion_settings.export_folder_name = 'notes'
    clean_filename = 'my-note.md'
    folder_name = "my-notebook"
    Path(tmp_path, config.DATA_DIR, conversion_settings.export_folder_name, folder_name, clean_filename).mkdir(parents=True, exist_ok=False)
    Path(tmp_path, config.DATA_DIR, conversion_settings.export_folder_name, folder_name, 'my-note-1.md').mkdir(parents=True, exist_ok=False)
    full_path = sn_note_writer.__generate_valid_output_path(conversion_settings, folder_name, clean_filename)
    assert full_path == Path(tmp_path, config.DATA_DIR, conversion_settings.export_folder_name, folder_name, 'my-note-2.md')


def test_generate_output_path(tmp_path):
    conversion_settings = ManualConversionSettings()
    conversion_settings.working_directory = tmp_path
    conversion_settings.export_format = 'html'
    title = 'My Note'
    folder_name = 'notes'
    result = sn_note_writer.generate_output_path(title, folder_name, conversion_settings).name
    assert result == 'my-note.html'


def test_store_file(tmp_path):
    file_path = Path(tmp_path, "test.txt")
    content = 'Hello World'
    sn_note_writer.store_file(file_path, content)

    result = file_path.read_text()
    assert result == content


@pytest.mark.parametrize('silent', [False, True])
def test_store_invalid_file(caplog, capsys, silent):
    config.set_silent(silent)
    file_path = Path('aklsjdh', "test.txt")
    content = 'Hello World'
    sn_note_writer.store_file(file_path, content)
    for record in caplog.records:
        assert record.levelname == "ERROR"
    captured = capsys.readouterr()
    if silent:
        assert captured.out == ""
    else:
        assert captured.out == f"Failed to write content to {file_path}\n"

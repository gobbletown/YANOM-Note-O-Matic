from mock import patch
import os
from pathlib import Path
import pytest

import config
import config_data
import conversion_settings
import file_converter_HTML_to_MD
import file_converter_MD_to_HTML
import file_converter_MD_to_MD
import notes_converter
import nsx_file_converter


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


@pytest.mark.parametrize(
    'conversion_count, message, expected', [
        (0, 'word', ''),
        (1, 'word', '1 word'),
        (2, 'word', '2 words')
    ]
)
def test_print_result_if_any(capsys, conversion_count, message, expected):
    args = ''
    nc = notes_converter.NotesConvertor(args, 'config_data_fake')

    nc.print_result_if_any(conversion_count, message)

    captured = capsys.readouterr()

    assert expected in captured.out


def test_log_results(caplog):
    args = ''
    nc = notes_converter.NotesConvertor(args, 'config_data_fake')
    nc._note_book_count = 1
    nc._note_page_count = 2
    nc._image_count = 3
    nc._attachment_count = 4

    caplog.clear()
    nc.log_results()

    assert len(caplog.records) == 4
    assert caplog.records[3].message == '4 Attachments'
    assert caplog.records[2].message == '3 Images'
    assert caplog.records[1].message == '2 Note Pages'
    assert caplog.records[0].message == '1 Note books'


def test_output_results_if_not_silent_mode_when_in_silent_mode(capsys):
    args = ''
    nc = notes_converter.NotesConvertor(args, 'config_data_fake')
    nc._note_book_count = 1
    nc._note_page_count = 2
    nc._image_count = 3
    nc._attachment_count = 4

    config.set_silent(True)

    nc.output_results_if_not_silent_mode()

    captured = capsys.readouterr()
    assert captured.out == ''


class FakeNSXFile:
    def __init__(self):
        self.inter_note_link_processor = FakeInterLinkProcessor()
        self.note_page_count = 1
        self.note_book_count = 2
        self.image_count = 3
        self.attachment_count = 4

    @staticmethod
    def process_nsx_file():
        print('nsx_file process_nsx_file called')
        return


class FakeInterLinkProcessor:
    def __init__(self):
        self.renamed_links_not_corrected = [1, 2]
        self.replacement_links = [1, 2, 3]
        self.unmatched_links_msg = "missing links message"


def test_output_results_if_not_silent_mode(capsys):
    args = ''
    nc = notes_converter.NotesConvertor(args, 'config_data_fake')
    nc._note_book_count = 1
    nc._note_page_count = 2
    nc._image_count = 3
    nc._attachment_count = 4
    nc._nsx_backups = [FakeNSXFile()]

    config.set_silent(False)

    nc.output_results_if_not_silent_mode()

    captured = capsys.readouterr()
    assert captured.out == '1 Note book\n2 Note pages\n3 Images\n4 Attachments\n3 out of 5 links between notes were re-created\nmissing links message\n'


class FakeConfigData:
    def __init__(self):
        self.conversion_settings = 'fake_conversion_settings'


def test_configure_for_ini_settings(caplog):
    args = ''
    nc = notes_converter.NotesConvertor(args, 'config_data_fake')
    nc.config_data = FakeConfigData()

    caplog.clear()

    nc.configure_for_ini_settings()

    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'Using settings from config  ini file'
    assert nc.conversion_settings == 'fake_conversion_settings'


def test_run_interactive_command_line_interface(caplog):
    test_source_path = str(Path(__file__).parent.absolute())
    args = {'source': test_source_path}
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()

    with patch('interactive_cli.StartUpCommandLineInterface.run_cli', spec=True,
               return_value=nc.conversion_settings) as mock_run_cli:
        caplog.clear()
        nc.run_interactive_command_line_interface()

        mock_run_cli.assert_called_once()
        assert nc.conversion_settings.source == Path(test_source_path)
        assert nc.config_data.conversion_settings.source == Path(test_source_path)
        assert len(caplog.records) == 3
        assert caplog.records[2].message == 'Using conversion settings from interactive command line tool'


def test_evaluate_command_line_arguments_when_wil_be_interactive_command_line_used(caplog):
    test_source_path = str(Path(__file__).parent.absolute())
    config.set_logger_level("DEBUG")
    args = {'silent': False, 'ini': False, 'source': test_source_path}
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)

    with patch('notes_converter.NotesConvertor.configure_for_ini_settings', spec=True,
               ) as mock_configure_for_ini_settings:
        with patch('notes_converter.NotesConvertor.run_interactive_command_line_interface', spec=True,
                   ) as mock_run_interactive_command_line_interface:
            caplog.clear()
            nc.evaluate_command_line_arguments()

            mock_configure_for_ini_settings.assert_called_once()
            mock_run_interactive_command_line_interface.assert_called_once()

            assert len(caplog.records) == 1

            assert 'Starting interactive command line tool' in caplog.records[0].message


@pytest.mark.parametrize(
    'silent, ini', [
        (True, True),
        (True, False),
        (False, True),
    ]
)
def test_evaluate_command_line_arguments_when_gogin_to_use_ini_file(caplog, silent, ini):
    test_source_path = str(Path(__file__).parent.absolute())
    config.set_logger_level("DEBUG")
    args = {'silent': silent, 'ini': ini, 'source': test_source_path}
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)

    with patch('notes_converter.NotesConvertor.configure_for_ini_settings', spec=True,
               ) as mock_configure_for_ini_settings:
        with patch('notes_converter.NotesConvertor.run_interactive_command_line_interface', spec=True,
                   ) as mock_run_interactive_command_line_interface:
            caplog.clear()
            nc.evaluate_command_line_arguments()

            mock_configure_for_ini_settings.assert_called_once()
            mock_run_interactive_command_line_interface.assert_not_called()

            assert len(caplog.records) == 0


def test_update_processing_stats():
    test_source_path = str(Path(__file__).parent.absolute())
    args = {'source': test_source_path}
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)

    nc.update_processing_stats(FakeNSXFile())
    assert nc._note_page_count == 1
    assert nc._note_book_count == 2
    assert nc._image_count == 3
    assert nc._attachment_count == 4


def test_process_nsx_files(capsys):
    test_source_path = str(Path(__file__).parent.absolute())
    args = {'source': test_source_path}
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)

    nc._nsx_backups = [FakeNSXFile()]

    nc.process_nsx_files()

    captured = capsys.readouterr()
    assert 'nsx_file process_nsx_file called' in captured.out
    assert nc._note_page_count == 1
    assert nc._note_book_count == 2
    assert nc._image_count == 3
    assert nc._attachment_count == 4


@pytest.mark.parametrize(
    'filetype', ['nsx', 'html']
)
def test_generate_file_list_multiple_files(tmp_path, filetype):
    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, f'file1.{filetype}'))
    touch(Path(tmp_path, f'file2.{filetype}'))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings.source = Path(tmp_path)

    result = nc.generate_file_list(f'{filetype}')

    assert len(result) == 2
    assert Path(tmp_path, f'file1.{filetype}') in result
    assert Path(tmp_path, f'file2.{filetype}') in result


def test_generate_file_list_single_file_source(tmp_path):
    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, 'file1.nsx'))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings.source = Path(tmp_path, 'file1.nsx')

    result = nc.generate_file_list('nsx')

    assert len(result) == 1
    assert Path(tmp_path, f'file1.nsx') in result


def test_convert_nsx(tmp_path, capsys):
    file_converter_type = nsx_file_converter.NSXFile

    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, 'file1.nsx'))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings.source = Path(tmp_path, 'file1.nsx')

    with patch('notes_converter.NotesConvertor.process_nsx_files', spec=True) as mock_process_nsx_files:
        nc.convert_nsx()

    mock_process_nsx_files.assert_called_once()
    assert len(nc._nsx_backups) == 1
    assert isinstance(nc._nsx_backups[0], nsx_file_converter.NSXFile)


def test_convert_html(tmp_path, capsys):
    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, 'file1.html'))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings._source = Path(tmp_path, 'file1.html')
    nc.conversion_settings._source_absolute_path = Path(tmp_path)

    nc.convert_html()

    assert Path(tmp_path, 'file1.md').exists()


def test_process_files(tmp_path):
    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, 'file1.html'))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings._source = Path(tmp_path, 'file1.html')
    nc.conversion_settings._source_absolute_path = Path(tmp_path)

    files_to_convert = [Path(tmp_path, 'file1.html')]
    file_converter = file_converter_HTML_to_MD.HTMLToMDConverter(nc.conversion_settings, files_to_convert)

    nc.process_files(files_to_convert, file_converter)

    assert nc._note_page_count == 1


@pytest.mark.parametrize(
    'silent_mode, expected_out', [
        (True, ''),
        (False, f" files found at path")
    ]
)
def test_exit_if_no_files_found_with_no_file(tmp_path, caplog, silent_mode, expected_out):
    config.set_silent(silent_mode)
    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, 'file1.html'))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings._source = Path(tmp_path)

    files_to_convert = None
    extension = 'html'

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        caplog.clear()
        nc.exit_if_no_files_found(files_to_convert, extension)

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0

    assert len(caplog.records) == 1
    assert expected_out in caplog.records[0].message


@pytest.mark.parametrize(
    'input_file, file_converter_type, export_format', [
        ('file1.md', file_converter_MD_to_MD.MDToMDConverter, 'gfm'),
        ('file1.md', file_converter_MD_to_HTML.MDToHTMLConverter, 'html'),
    ]
)
def test_convert_markdown(tmp_path, input_file, file_converter_type, export_format):
    test_source_path = tmp_path
    args = {'source': test_source_path}
    touch(Path(tmp_path, input_file))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings._source = Path(tmp_path, input_file)
    nc.conversion_settings._source_absolute_path = Path(tmp_path)
    nc.conversion_settings.export_format = export_format

    with patch('notes_converter.NotesConvertor.process_files', spec=True) as mock_process_files:
        nc.convert_markdown()

    args = mock_process_files.call_args.args
    assert args[0] == [Path(tmp_path, input_file)]
    assert isinstance(args[1], file_converter_type)


@pytest.mark.parametrize(
    'input_file, file_converter_type, export_format, conversion_input', [
        ('file1.md', file_converter_MD_to_MD.MDToMDConverter, 'gfm', 'markdown'),
        ('file1.html', file_converter_HTML_to_MD.HTMLToMDConverter, 'html', 'html'),
        ('file1.md', file_converter_MD_to_HTML.MDToHTMLConverter, 'html', 'markdown')
    ]
)
def test_convert_notes(tmp_path, input_file, file_converter_type, export_format, conversion_input):
    test_source_path = tmp_path
    args = {'silent': True, 'ini': False, 'source': test_source_path}
    touch(Path(tmp_path, input_file))
    nc = notes_converter.NotesConvertor(args, 'config_data')
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings._source = Path(tmp_path, input_file)
    nc.conversion_settings._working_directory = Path(tmp_path)
    nc.conversion_settings._source_absolute_path = Path(tmp_path)
    nc.conversion_settings.export_format = export_format
    nc.conversion_settings.conversion_input = conversion_input

    with patch('notes_converter.NotesConvertor.process_files', spec=True) as mock_process_files:
        with patch('notes_converter.NotesConvertor.evaluate_command_line_arguments', spec=True) as mock_evaluate_command_line_arguments:
            nc.convert_notes()

            mock_evaluate_command_line_arguments.assert_called_once()
            mock_evaluate_command_line_arguments.assert_called_once()
            mock_process_files.assert_called_once()
            args = mock_process_files.call_args.args
            assert args[0] == [Path(tmp_path, input_file)]
            assert isinstance(args[1], file_converter_type)


def test_convert_notes_nsx_file_type(tmp_path, capsys, caplog):
    test_source_path = tmp_path
    input_file = 'file1.md'
    args = {'silent': True, 'ini': False, 'source': test_source_path}
    touch(Path(tmp_path, input_file))
    cd = config_data.ConfigData(f"{config.DATA_DIR}/config.ini", 'gfm', allow_no_value=True)
    nc = notes_converter.NotesConvertor(args, cd)
    nc.conversion_settings = conversion_settings.ConversionSettings()
    nc.conversion_settings._source = Path(tmp_path, input_file)
    nc.conversion_settings._source_absolute_path = Path(tmp_path)
    nc.conversion_settings.conversion_input = 'nsx'

    with patch('notes_converter.NotesConvertor.process_nsx_files', spec=True) as mock_process_nsx_files:
        with patch('notes_converter.NotesConvertor.evaluate_command_line_arguments', spec=True) as mock_evaluate_command_line_arguments:
            caplog.clear()
            nc.convert_notes()

    mock_process_nsx_files.assert_called_once()
    assert len(nc._nsx_backups) == 1

    captured = capsys.readouterr()

    assert 'Processing Completed' in caplog.records[-1].message
    assert 'Found pandoc' in captured.out

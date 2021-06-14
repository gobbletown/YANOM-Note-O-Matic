from mock import patch
from pathlib import Path

import config
import pytest

import nsx_pre_processing
import pandoc_converter
import sn_note_page


@pytest.fixture
def note_page(nsx):
    note_jason = {'parent_id': 'note_book2', 'title': 'Page 8 title',
                  'mtime': 1619298640, 'ctime': 1619298559, 'attachment': {'test': 'test_value'}, 'content': 'content',
                  'tag': [9]}
    np = sn_note_page.NotePage(nsx, '1234', note_jason)
    return np


@pytest.fixture
def note_page_1(nsx):
    note_page_1_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539,
                        'content': 'content', 'tag': [1], 'attachment': {
            "_-m4Hhgmp34U85IwTdWfbWw": {"md5": "e79072f793f22434740e64e93cfe5926",
                                        "name": "ns_attach_image_787491613404344687.png", "size": 186875, "width": 1848,
                                        "height": 1306, "type": "image/png", "ctime": 1616084097,
                                        "ref": "MTYxMzQwNDM0NDczN25zX2F0dGFjaF9pbWFnZV83ODc0OTE2MTM0MDQzNDQ2ODcucG5n"},
            "_YOgkfaY7aeHcezS-jgGSmA": {"md5": "6c4b828f227a096d3374599cae3f94ec",
                                        "name": "Record 2021-02-15 16:00:13.webm", "size": 9627, "width": 0,
                                        "height": 0, "type": "video/webm", "ctime": 1616084097},
            "_yITQrdarvsdg3CkL-ifh4Q": {"md5": "c4ee8b831ad1188509c0f33f0c072af5", "name": "example-attachment.pdf",
                                        "size": 14481, "width": 0, "height": 0, "type": "application/pdf",
                                        "ctime": 1616084097},
            "file_dGVzdCBwYWdlLnBkZjE2MTkyOTg3MjQ2OTE=": {"md5": "27a9aadc878b718331794c8bc50a1b8c",
                                                          "name": "test page.pdf", "size": 320357, "width": 0,
                                                          "height": 0, "type": "application/pdf", "ctime": 1619295124}}}
    note_page_1 = sn_note_page.NotePage(nsx, 1, note_page_1_json)
    note_page_1.notebook_folder_name = 'note_book1'
    note_page_1._file_name = 'page-1-title.md'
    note_page_1._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div>"""

    return note_page_1


@pytest.mark.parametrize(
    'front_matter_format, creation_time_in_exported_file_name, expected_ctime, expected_mtime', [
        ('none', False, 1619298559, 1619298640),
        ('none', True, '202104242209', '202104242210'),
        ('yaml', True, '202104242209', '202104242210'),
        ('yaml', False, '202104242209', '202104242210'),
    ]
)
def test_init_note_page(nsx, front_matter_format, creation_time_in_exported_file_name, expected_ctime, expected_mtime):
    nsx.conversion_settings.front_matter_format = front_matter_format
    nsx.conversion_settings.creation_time_in_exported_file_name = creation_time_in_exported_file_name
    note_jason = {'parent_id': 'note_book2', 'title': 'Page 8 title',
                  'mtime': 1619298640, 'ctime': 1619298559, 'attachment': {'test': 'test_value'}, 'content': 'content',
                  'tag': [9]}
    note_page = sn_note_page.NotePage(nsx, '1234', note_jason)

    assert note_page.note_json['ctime'] == expected_ctime
    assert note_page.note_json['mtime'] == expected_mtime

    assert note_page.title == 'Page 8 title'
    assert note_page.original_title == 'Page 8 title'
    assert note_page.raw_content == 'content'
    assert note_page.parent_notebook == 'note_book2'
    assert note_page._attachments_json == {'test': 'test_value'}


@pytest.mark.parametrize(
    'export_format, extension', [
        ('html', 'html'),
        ('gfm', 'md'),
    ]
)
def test_generate_filenames_and_paths(export_format, extension, note_page):
    note_page.conversion_settings.export_format = export_format
    note_page.notebook_folder_name = 'note_book2'

    note_page.generate_filenames_and_paths()

    assert note_page.file_name == f'page-8-title.{extension}'
    assert note_page.full_path == Path(note_page.conversion_settings.working_directory, config.DATA_DIR,
                                       note_page.conversion_settings.export_folder_name, note_page.notebook_folder_name,
                                       note_page.file_name)


def test_create_attachments(nsx, note_page_1):
    with patch('sn_attachment.ImageNSAttachment', spec=True):
        with patch('sn_attachment.FileNSAttachment', spec=True):
            image_count, file_count = note_page_1.create_attachments()

    assert image_count == 1
    assert file_count == 3


def test_process_attachments(nsx, note_page_1):
    with patch('sn_attachment.ImageNSAttachment', spec=True) as mock_image_attachment:
        with patch('sn_attachment.FileNSAttachment', spec=True) as mock_file_attachment:
            _ignored_1, _ignored_2 = note_page_1.create_attachments()

            note_page_1.process_attachments()

            mock_image_attachment.assert_called_once()
            assert mock_file_attachment.call_count == 3


def test_pre_process_content(note_page):
    note_page.pre_process_content()

    assert note_page.pre_processed_content == '<head><title> </title></head>content'


@pytest.mark.parametrize(
    'export_format, expected', [
        ('html', '<head><title> </title></head>content'),
        ('gfm', 'content\n'),
    ]
)
def test_convert_data(note_page, export_format, expected):
    note_page.conversion_settings.export_format = export_format
    note_page._pre_processed_content = '<head><title> </title></head>content'
    note_page._pandoc_converter = pandoc_converter.PandocConverter(note_page.conversion_settings)
    note_page.convert_data()

    assert note_page._converted_content == expected


def test_post_process_content(note_page, tmp_path):
    note_page._pre_processed_content = '<head><title> </title></head>content'
    note_page._pandoc_converter = pandoc_converter.PandocConverter(note_page.conversion_settings)
    note_page._converted_content = 'content\n'
    note_page._pre_processor = nsx_pre_processing.NoteStationPreProcessing(note_page)
    note_page.post_process_content()

    assert note_page._converted_content == 'content\n\n'


@pytest.mark.parametrize(
    'title_list, expected_new_title', [
        (['no_match', 'no_match2'], 'Page 8 title'),
        (['no_match', 'no_match2', 'Page 8 title'], 'Page 8 title-1'),
    ]
)
def test_increment_duplicated_title(note_page, title_list, expected_new_title):
    note_page.increment_duplicated_title(title_list)

    assert note_page.title == expected_new_title


@pytest.mark.parametrize(
    'export_format, expected', [
        ('gfm',
         """Below is a hyperlink to the internet\n\n<https://github.com/kevindurston21/YANOM-Note-O-Matic>\n\n###### Attachments\n\n[record-2021-02-15-160013.webm](attachments/record-2021-02-15-160013.webm)\n\n[example-attachment.pdf](attachments/example-attachment.pdf)\n\n[test-page.pdf](attachments/test-page.pdf)\n\n"""),
        ('html',
         """<head><title> </title></head><p>Below is a hyperlink to the internet</p><p><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></p><h6>Attachments</h6><p><a href="attachments/record-2021-02-15-160013.webm">record-2021-02-15-160013.webm</a></p><p><a href="attachments/example-attachment.pdf">example-attachment.pdf</a></p><p><a href="attachments/test-page.pdf">test-page.pdf</a></p>"""),
    ]
)
def test_process_note(nsx, note_page_1, export_format, expected):
    note_page_1.conversion_settings.export_format = export_format
    note_page_1._pandoc_converter = pandoc_converter.PandocConverter(note_page_1.conversion_settings)

    note_page_1.process_note()

    assert note_page_1.converted_content == expected

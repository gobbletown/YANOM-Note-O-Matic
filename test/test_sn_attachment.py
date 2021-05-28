from pathlib import Path

import pytest

import sn_attachment
import conversion_settings


class NSXFile:
    @staticmethod
    def fetch_attachment_file(ignored):
        return 'file name in nsx'

class Note:
    def __init__(self):
        self.nsx_file = NSXFile()
        self.conversion_settings = conversion_settings.ConversionSettings()
        self.note_json = {'attachment':
                              {'1234':
                                   {'ref': '54321',
                                    'md5': 'qwerty',
                                    'name': 'my_name'
                                    }
                               }
                          }
        self.notebook_folder_name = 'notebook_folder'


def test_FileNSAttachment_create_html_link():
    note = Note()
    attachment_id = '1234'
    file_attachment = sn_attachment.FileNSAttachment(note, attachment_id)

    file_attachment._file_name = 'my_file.png'
    file_attachment._path_relative_to_notebook = 'attachments/my_file.png'
    file_attachment.create_html_link()

    assert file_attachment.html_link == '<a href="attachments/my_file.png">my_file.png</a>'


@pytest.mark.parametrize(
    'raw_name, expected', [
        ('my_file.png', 'my_file.png'),
        ('my file.png', 'my-file.png'),
        ],
    ids=['clean-file-name', 'file-name-to-clean']
)
def test_FileNSAttachment_create_file_name(raw_name, expected):
    note = Note()
    attachment_id = '1234'
    file_attachment = sn_attachment.FileNSAttachment(note, attachment_id)

    file_attachment._name = raw_name
    file_attachment.create_file_name()

    assert file_attachment.file_name == Path(expected)

def test_FileNSAttachment_get_content_to_save():
    note = Note()
    attachment_id = '1234'
    file_attachment = sn_attachment.FileNSAttachment(note, attachment_id)
    result = file_attachment.get_content_to_save()

    assert result == 'file name in nsx'


def test_ImageNSAttachment_create_html_link():
    note = Note()
    attachment_id = '1234'
    image_attachment = sn_attachment.ImageNSAttachment(note, attachment_id)

    image_attachment._file_name = 'my_file.png'
    image_attachment.create_html_link()

    assert image_attachment.html_link == f'<img src="my_file.png" >'

@pytest.mark.parametrize(
    'raw_name, expected', [
        ('ns_attach_image_my_file.png', 'my_file.png'),
        ('ns_attach_image_my file.png', 'my-file.png'),
        ],
    ids=['clean-file-name', 'file-name-to-clean']
)
def test_ImageNSAttachment_create_file_name(raw_name, expected):
    note = Note()
    attachment_id = '1234'
    image_attachment = sn_attachment.ImageNSAttachment(note, attachment_id)

    image_attachment._name = raw_name
    image_attachment.create_file_name()

    assert image_attachment.file_name == Path(expected)


def test_ImageNSAttachment_image_ref():
    note = Note()
    attachment_id = '1234'
    image_attachment = sn_attachment.ImageNSAttachment(note, attachment_id)

    assert image_attachment.image_ref == '54321'


def test_change_file_name_if_already_exists(tmp_path):
    note = Note()
    attachment_id = '1234'
    image_attachment = sn_attachment.ImageNSAttachment(note, attachment_id)

    image_attachment._full_path = Path(tmp_path, 'my_file.png')

    image_attachment._full_path.write_text('hello world')

    image_attachment.change_file_name_if_already_exists()

    assert len(str(image_attachment.full_path)) == len(str(Path(tmp_path, 'my_file.png'))) + 5  # 4 random chars and a dash


def test_notebook_folder_name():
    note = Note()
    attachment_id = '1234'
    image_attachment = sn_attachment.ImageNSAttachment(note, attachment_id)

    assert image_attachment.notebook_folder_name == 'notebook_folder'




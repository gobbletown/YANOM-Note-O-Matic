from mock import patch
from pathlib import Path

import pytest

import image_processing


@pytest.mark.parametrize(
    'content, generate_format, expected', [
        ("""![|600](attachments/787491613404344687.png)""",
         """gfm""",
         """<img src="attachments/787491613404344687.png" width="600">"""),
        ("""<img src="attachments/787491613404344687.png" width="600">""",
         """obsidian""",
         """![|600](attachments/787491613404344687.png)""")
    ], ids=['obsidian-gfm', 'nsx-obsidian']
)
def test_obsidian_image_tag_formatter_class(content, generate_format, expected):
    obsidian_tag_formatter = image_processing.ObsidianImageTagFormatter(content, generate_format)

    assert obsidian_tag_formatter.processed_content == expected


class ImageNSAttachment:
    """Fake class to allow testing of ImageTag class"""

    def __init__(self):
        self.image_ref = 'MTYxMzQwNDM0NDczN25zX2F0dGFjaF9pbWFnZV83ODc0OTE2MTM0MDQzNDQ2ODcucG5n'
        self.path_relative_to_notebook = Path('attachments/12345678.png')


@pytest.mark.parametrize(
    'raw_tag, expected', [
        ("""<img class=\" syno-notestation-image-object\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" border=\"0\" width=\"600\" ref=\"MTYxMzQwNDM0NDczN25zX2F0dGFjaF9pbWFnZV83ODc0OTE2MTM0MDQzNDQ2ODcucG5n\" adjust=\"true\" />""",
         """<img src="attachments/12345678.png" width="600">"""),
        ("""<img class=\" syno-notestation-image-object\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" border=\"0\" ref=\"MTYxMzQwNDM0NDczN25zX2F0dGFjaF9pbWFnZV83ODc0OTE2MTM0MDQzNDQ2ODcucG5n\" adjust=\"true\" />""",
         """<img src="attachments/12345678.png">""")],
    ids=['tag-with-width', 'tag-without-width']
)
def test_image_tag_class(raw_tag, expected):
    attachments = {'key': ImageNSAttachment()}

    with patch('image_processing.isinstance', return_value=True):
        image_tag_processor = image_processing.ImageTag(raw_tag, attachments)

    assert image_tag_processor.processed_tag == expected

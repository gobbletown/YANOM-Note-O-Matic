from mock import patch
import re

import pytest

import sn_note_page


@pytest.fixture
def note_1(nsx):
    note_page_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559,
                        'ctime': 1619298539,
                        'content': 'content', 'tag': [1], 'attachment': {
            "_-m4Hhgmp34U85IwTdWfbWw": {"md5": "e79072f793f22434740e64e93cfe5926",
                                        "name": "ns_attach_image_787491613404344687.png", "size": 186875,
                                        "width": 1848,
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
                                                          "height": 0, "type": "application/pdf",
                                                          "ctime": 1619295124}}}
    note_page = sn_note_page.NotePage(nsx, 1, note_page_json)
    note_page.notebook_folder_name = 'note_book1'
    note_page._file_name = 'page-1-title.md'
    note_page._raw_content = """<div>Pie Chart</div><div></div><div><div class=\"syno-ns-chart-object\" style=\"width: 520px; height: 350px;\" chart-data=\"[[&quot;&quot;,&quot;cost&quot;,&quot;price&quot;,&quot;value&quot;,&quot;total value&quot;],[&quot;something&quot;,500,520,540,520],[&quot;something else&quot;,520,540,560,540],[&quot;another thing&quot;,540,560,580,560]]\" chart-config=\"{&quot;range&quot;:&quot;A1:E4&quot;,&quot;direction&quot;:&quot;row&quot;,&quot;rowHeaderExisted&quot;:true,&quot;columnHeaderExisted&quot;:true,&quot;title&quot;:&quot;Pie chart title&quot;,&quot;chartType&quot;:&quot;pie&quot;,&quot;xAxisTitle&quot;:&quot;x-axis title&quot;,&quot;yAxisTitle&quot;:&quot;y axis ttile&quot;}\"></div></div><div><iframe src=\"https://www.youtube.com/embed/SqdxNUMO2cg\" width=\"420\" height=\"315\" frameborder=\"0\" allowfullscreen=\"\" youtube=\"true\" anchorhref=\"https://www.youtube.com/watch?v=SqdxNUMO2cg\">&nbsp;</iframe></div><div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a 3x3 Table</div><div><table style=\"width: 240px; height: 90px;\"><tbody><tr><td><b>cell R1C1</b></td><td><b>cell R1C2</b></td><td><b>cell R1C3</b></td></tr><tr><td>cell R2C1</td><td>cell R1C2</td><td>cell R1C3</td></tr><tr><td>cell R3C1</td><td>cell R1C2</td><td>cell R1C3</td></tr></tbody></table></div><div>Below&nbsp;is an image of the design of the&nbsp;line chart as seen in note-station</div><div><img class=\" syno-notestation-image-object\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" border=\"0\" width=\"600\" ref=\"MTYxMzQwNDM0NDczN25zX2F0dGFjaF9pbWFnZV83ODc0OTE2MTM0MDQzNDQ2ODcucG5n\" adjust=\"true\" /></div>"""

    return note_page


def test_pre_process_note_page(note_1):
    with patch('sn_attachment.ImageNSAttachment.store_attachment', spec=True):
        with patch('sn_attachment.FileNSAttachment.store_attachment', spec=True):
            note_1.pre_process_content()

            output_html_regx = r"""<head><title> </title></head><p>Pie Chart</p><p></p><p><p><img src='attachments/\d{15}\.png'></p><p><a href='attachments/\d{15}\.csv'>Chart data file</a></p><p><table border="1" class="dataframe"><thead><tr style="text-align: right;"><th><strong></strong></th><th><strong>cost</strong></th><th><strong>price</strong></th><th><strong>value</strong></th><th><strong>total value</strong></th><th><strong>sum</strong></th><th><strong>percent</strong></th></tr></thead><tbody><tr><th><strong>something</strong></th><td>500</td><td>520</td><td>540</td><td>520</td><td>2080</td><td>32.10</td></tr><tr><th><strong>something else</strong></th><td>520</td><td>540</td><td>560</td><td>540</td><td>2160</td><td>33.33</td></tr><tr><th><strong>another thing</strong></th><td>540</td><td>560</td><td>580</td><td>560</td><td>2240</td><td>34.57</td></tr></tbody></table></p></p><p>iframe-placeholder-id-\d{15}</p><p>Below is a hyperlink to the internet</p><p><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></p><p>Below is a 3x3 Table</p><p><table border="1" style="width: 240px; height: 90px;"><thead><tr><td><strong>cell R1C1</strong></td><td><strong>cell R1C2</strong></td><td><strong>cell R1C3</strong></td></tr></thead><tbody><tr><td><strong>cell R2C1</strong></td><td>cell R1C2</td><td>cell R1C3</td></tr><tr><td><strong>cell R3C1</strong></td><td>cell R1C2</td><td>cell R1C3</td></tr></tbody></table></p><p>Below is an image of the design of the line chart as seen in note-station</p><p><img src="" width="600"/></p>"""

            result = note_1.pre_processed_content
            match = re.findall(output_html_regx, result)
            # Note output_html_regx string uses '\d{15}\' to replace the id numbers in the actual html output
            # and escapes the full stop before the file extension

            assert result == match[0]


def test_pre_process_note_page_1(note_1):
    note_1.conversion_settings.first_row_as_header = False
    note_1.conversion_settings.first_column_as_header = False
    note_1.conversion_settings.front_matter_format = 'none'

    with patch('sn_attachment.ImageNSAttachment.store_attachment', spec=True):
        with patch('sn_attachment.FileNSAttachment.store_attachment', spec=True):
            note_1.pre_process_content()

            output_html_regx = """<p>Pie Chart</p><p></p><p><p><img src='attachments/\d{15}\.png'></p><p><a href='attachments/\d{15}\.csv'>Chart data file</a></p><p><table border="1" class="dataframe"><thead><tr style="text-align: right;"><th><strong></strong></th><th><strong>cost</strong></th><th><strong>price</strong></th><th><strong>value</strong></th><th><strong>total value</strong></th><th><strong>sum</strong></th><th><strong>percent</strong></th></tr></thead><tbody><tr><th><strong>something</strong></th><td>500</td><td>520</td><td>540</td><td>520</td><td>2080</td><td>32.10</td></tr><tr><th><strong>something else</strong></th><td>520</td><td>540</td><td>560</td><td>540</td><td>2160</td><td>33.33</td></tr><tr><th><strong>another thing</strong></th><td>540</td><td>560</td><td>580</td><td>560</td><td>2240</td><td>34.57</td></tr></tbody></table></p></p><p>iframe-placeholder-id-\d{15}</p><p>Below is a hyperlink to the internet</p><p><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></p><p>Below is a 3x3 Table</p><p><table border="1" style="width: 240px; height: 90px;"><tbody><tr><td><b>cell R1C1</b></td><td><b>cell R1C2</b></td><td><b>cell R1C3</b></td></tr><tr><td>cell R2C1</td><td>cell R1C2</td><td>cell R1C3</td></tr><tr><td>cell R3C1</td><td>cell R1C2</td><td>cell R1C3</td></tr></tbody></table></p><p>Below is an image of the design of the line chart as seen in note-station</p><p><img src="" width="600"/></p>"""

            result = note_1.pre_processed_content
            match = re.findall(output_html_regx, result)
            # Note output_html_regx string uses '\d{15}\' to replace the chart id number in the actual html output
            # and escapes the full stop before the file extension

            assert result == match[0]

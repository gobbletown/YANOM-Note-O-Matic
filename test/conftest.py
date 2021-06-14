import pytest

import conversion_settings
import nsx_file_converter
import pandoc_converter
import sn_note_page


@pytest.fixture
def all_notes(nsx):
    list_of_notes = []
    # Note with no links
    note_page_1_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'content': 'content', 'tag': [1], 'attachment': {"_-m4Hhgmp34U85IwTdWfbWw": {"md5": "e79072f793f22434740e64e93cfe5926", "name": "ns_attach_image_787491613404344687.png", "size": 186875, "width": 1848, "height": 1306, "type": "image/png", "ctime":1616084097, "ref":"MTYxMzQwNDM0NDczN25zX2F0dGFjaF9pbWFnZV83ODc0OTE2MTM0MDQzNDQ2ODcucG5n"}, "_YOgkfaY7aeHcezS-jgGSmA": {"md5":"6c4b828f227a096d3374599cae3f94ec", "name": "Record 2021-02-15 16:00:13.webm", "size": 9627, "width": 0, "height": 0, "type": "video/webm", "ctime": 1616084097}, "_yITQrdarvsdg3CkL-ifh4Q": {"md5": "c4ee8b831ad1188509c0f33f0c072af5", "name": "example-attachment.pdf", "size": 14481, "width": 0, "height": 0, "type": "application/pdf", "ctime": 1616084097},"file_dGVzdCBwYWdlLnBkZjE2MTkyOTg3MjQ2OTE=": {"md5":"27a9aadc878b718331794c8bc50a1b8c", "name": "test page.pdf", "size": 320357, "width": 0, "height": 0, "type": "application/pdf", "ctime": 1619295124}}}
    note_page_1 = sn_note_page.NotePage(nsx, 1, note_page_1_json)
    note_page_1.notebook_folder_name = 'note_book1'
    note_page_1._file_name = 'page-1-title.md'
    note_page_1._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div>"""
    list_of_notes.append(note_page_1)

    # note with link to note in different notebook
    note_page_2_json = {'parent_id': 'note_book1', 'title': 'Page 2 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [2]}
    note_page_2 = sn_note_page.NotePage(nsx, 1, note_page_2_json)
    note_page_2.notebook_folder_name = 'note_book1'
    note_page_2._file_name = 'page-2-title.md'
    note_page_2._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 8</div><div><a href=\"notestation://remote/self/1234-8\">Page 8 title</a></div>"""
    list_of_notes.append(note_page_2)

    # note with link to note in same notebook
    note_page_3_json = {'parent_id': 'note_book1', 'title': 'Page 3 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [3]}
    note_page_3 = sn_note_page.NotePage(nsx, 1, note_page_3_json)
    note_page_3.notebook_folder_name = 'note_book1'
    note_page_3._file_name = 'pag3-3-title.md'
    note_page_3._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 title</a></div>"""
    list_of_notes.append(note_page_3)

    # note with link to renamed link to page in same notebook when there is also another good link on another page
    note_page_4_json = {'parent_id': 'note_book1', 'title': 'Page 4 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [4]}
    note_page_4 = sn_note_page.NotePage(nsx, 1, note_page_4_json)
    note_page_4.notebook_folder_name = 'note_book1'
    note_page_4._file_name = 'page-4-title.md'
    note_page_4._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link ranamed link to page 1</div><div><a href=\"notestation://remote/self/1234-2\">Page 1 renamed</a></div>"""
    list_of_notes.append(note_page_4)

    # note with link to renamed link to page in different notebook that is also a duplicated title
    note_page_5_json = {'parent_id': 'note_book1', 'title': 'Page 5 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [5]}
    note_page_5 = sn_note_page.NotePage(nsx, 1, note_page_5_json)
    note_page_5.notebook_folder_name = 'note_book1'
    note_page_5._file_name = 'page-5-title.md'
    note_page_5._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a renamed link to page 8</div><div><a href=\"notestation://remote/self/1234-8\">Page 8 renamed</a></div>"""
    list_of_notes.append(note_page_5)

    # note with duplicated title across 2 notebooks - first duplicate
    note_page_6_json = {'parent_id': 'note_book1', 'title': 'Duplicate page title across notebooks', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [6]}
    note_page_6 = sn_note_page.NotePage(nsx, 1, note_page_6_json)
    note_page_6.notebook_folder_name = 'note_book1'
    note_page_6._file_name = 'duplicate-page-title2.md'
    note_page_6._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to duplicated title across 2 notebooks</div><div><a href=\"notestation://remote/self/1234-7\">Page 5 title</a></div>"""
    list_of_notes.append(note_page_6)

    # note with duplicated title across 2 notebooks - second duplicate
    note_page_7_json = {'parent_id': 'note_book2', 'title': 'Duplicate page title across notebooks', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [7]}
    note_page_7 = sn_note_page.NotePage(nsx, 1, note_page_7_json)
    note_page_7.notebook_folder_name = 'note_book2'
    note_page_7._file_name = 'duplicate-page-title2-1.md'
    note_page_7._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to duplicated title across 2 notebooks</div><div><a href=\"notestation://remote/self/1234-6\">Page 5 title</a></div>"""
    list_of_notes.append(note_page_7)

    # note with duplicate title to note page in same notebook - first page
    note_page_8_json = {'parent_id': 'note_book2', 'title': 'Page 8 title',
                        'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [8]}
    note_page_8 = sn_note_page.NotePage(nsx, 1, note_page_8_json)
    note_page_8.notebook_folder_name = 'note_book2'
    note_page_8._file_name = 'page-8-title.md'
    note_page_8._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href=\"notestation://remote/self/1234-2\">Page 2 title</a></div>"""
    list_of_notes.append(note_page_8)

    # note with duplicate title to note page in same notebook - second page
    note_page_9_json = {'parent_id': 'note_book2', 'title': 'Page 8 title',
                        'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [9]}
    note_page_9 = sn_note_page.NotePage(nsx, 1, note_page_9_json)
    note_page_9.notebook_folder_name = 'note_book2'
    note_page_9._file_name = 'page-8-title-1.md'
    note_page_9._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href=\"notestation://remote/self/1234-2\">Page 2 title</a></div>"""
    list_of_notes.append(note_page_9)

    # note to be linked to from a renamed page, note this page must have no good links pointing to it - first page
    note_page_10_json = {'parent_id': 'note_book2', 'title': 'Page 10 title',
                        'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [10]}
    note_page_10 = sn_note_page.NotePage(nsx, 1, note_page_10_json)
    note_page_10.notebook_folder_name = 'note_book2'
    note_page_10._file_name = 'page-10-title.md'
    note_page_10._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href=\"notestation://remote/self/1234-2\">Page 2 title</a></div>"""
    list_of_notes.append(note_page_10)

    # renamed link pointing to a page that has no good links pointing to it - second page
    note_page_11_json = {'parent_id': 'note_book2', 'title': 'Page 11 title',
                        'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [11]}
    note_page_11 = sn_note_page.NotePage(nsx, 1, note_page_11_json)
    note_page_11.notebook_folder_name = 'note_book2'
    note_page_11._file_name = 'page-11-title.md'
    note_page_11._raw_content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a renamed link to page 10</div><div><a href=\"notestation://remote/self/1234-10\">Page 10 renamed</a></div>"""
    list_of_notes.append(note_page_11)

    return list_of_notes


@pytest.fixture
def conv_setting(tmp_path):
    cs = conversion_settings.ConversionSettings()
    cs.working_directory = tmp_path
    return cs


@pytest.fixture
def nsx(conv_setting):
    nsx = nsx_file_converter.NSXFile('fake_file', conv_setting, pandoc_converter.PandocConverter(conv_setting))
    return nsx

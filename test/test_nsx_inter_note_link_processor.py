import pytest

import conversion_settings
import nsx_file_converter
import nsx_inter_note_link_processor
import sn_note_page


def all_notes(nsx):
    list_of_notes = []
    # Note with no links
    note_page_1_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': [1]}
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
def use_all_notes(nsx):
    return all_notes(nsx)


@pytest.fixture
def use_all_notes_expected():
    return """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 8</div><div><a href="../note_book2/page-8-title.md">Page 8 title</a><br><a href="../note_book2/page-8-title-1.md">Page 8 title</a><br></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link page 1</div><div><a href="page-1-title.md">Page 1 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link ranamed link to page 1</div><div><a href="page-2-title.md">Page 1 renamed</a><br><a href="page-2-title.md">Page 1 renamed</a><br><a href="page-2-title.md">Page 1 renamed</a><br></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a renamed link to page 8</div><div><a href="../note_book2/page-8-title.md">Page 8 renamed</a><br><a href="../note_book2/page-8-title-1.md">Page 8 renamed</a><br></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to duplicated title across 2 notebooks</div><div><a href="page-5-title.md">Page 5 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to duplicated title across 2 notebooks</div><div><a href="../note_book1/page-5-title.md">Page 5 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href="../note_book1/page-2-title.md">Page 2 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href="../note_book1/page-2-title.md">Page 2 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href="../note_book1/page-2-title.md">Page 2 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a renamed link to page 10</div><div><a href="notestation://remote/self/1234-10">Page 10 renamed</a></div>"""


@pytest.fixture
def use_only_title_matched_notes_expected():
    return """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href="../note_book1/page-2-title.md">Page 2 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href="../note_book1/page-2-title.md">Page 2 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 2</div><div><a href="../note_book1/page-2-title.md">Page 2 title</a></div><div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 8</div><div><a href="../note_book2/page-8-title-1.md">Page 8 title</a><br><a href="../note_book2/page-8-title.md">Page 8 title</a><br></div>"""


@pytest.fixture
def use_only_title_matched_notes(nsx):
    all_notes_to_trim = all_notes(nsx)
    title_matching_notes = [all_notes_to_trim[9], all_notes_to_trim[8], all_notes_to_trim[7], all_notes_to_trim[1]]
    return title_matching_notes


@pytest.fixture
def conv_setting():
    conv_setting = conversion_settings.ConversionSettings()
    return conv_setting


@pytest.fixture
def nsx(conv_setting):
    nsx = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')
    return nsx


def test_make_list_of_links(use_all_notes):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_all_notes)

    assert len(link_processor._replacement_links) == 10
    assert link_processor._replacement_links[0].raw_link == '<a href=\"notestation://remote/self/1234-8\">Page 8 title</a>'


def test_match_link_title_to_notes(use_all_notes):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_all_notes)
    link_processor.match_link_title_to_notes(use_all_notes)

    matched_links = [link for link in link_processor.replacement_links if link.target_notes]

    assert len(matched_links) == 7


def test_match_renamed_links_using_link_ref_id(use_all_notes, caplog):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_all_notes)
    link_processor.match_link_title_to_notes(use_all_notes)
    link_processor.match_renamed_links_using_link_ref_id()

    assert len(link_processor.replacement_links) == 9
    assert len(link_processor.renamed_links_not_corrected) == 1

    assert len(caplog.records) > 0
    for record in caplog.records:
        assert record.levelname == 'INFO'


def test_update_content(use_all_notes, use_all_notes_expected):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_all_notes)
    link_processor.match_link_title_to_notes(use_all_notes)
    link_processor.match_renamed_links_using_link_ref_id()

    content = ''
    for note in use_all_notes:
        content = f'{content}{note.raw_content}'

    result = link_processor.update_content(content)

    assert result == use_all_notes_expected

    message = link_processor.unmatched_links_msg

    assert message == 'The following link(s) could not be corrected.\nOn page - Page 11 title - <a href="notestation://remote/self/1234-10">Page 10 renamed</a>\n'

# Test below use notes only where links are valid title matches
def test_make_list_of_links_use_only_title_matched_notes(use_only_title_matched_notes):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_only_title_matched_notes)

    assert len(link_processor._replacement_links) == 4


def test_match_link_title_to_notes_use_only_title_matched_notes(use_only_title_matched_notes):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_only_title_matched_notes)
    link_processor.match_link_title_to_notes(use_only_title_matched_notes)

    matched_links = [link for link in link_processor.replacement_links if link.target_notes]

    assert len(matched_links) == 4


def test_match_renamed_links_using_link_ref_id_use_only_title_matched_notes(use_only_title_matched_notes, caplog):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_only_title_matched_notes)
    link_processor.match_link_title_to_notes(use_only_title_matched_notes)
    link_processor.match_renamed_links_using_link_ref_id()

    assert len(link_processor.replacement_links) == 4
    assert len(link_processor.renamed_links_not_corrected) == 0

    assert len(caplog.records) == 0


def test_update_content_use_only_title_matched_notes(use_only_title_matched_notes, use_only_title_matched_notes_expected):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_only_title_matched_notes)
    link_processor.match_link_title_to_notes(use_only_title_matched_notes)
    link_processor.match_renamed_links_using_link_ref_id()

    content = ''
    for note in use_only_title_matched_notes:
        content = f'{content}{note.raw_content}'

    result = link_processor.update_content(content)

    assert result == use_only_title_matched_notes_expected


def test_update_content_use_only_title_matched_notes_content_with_no_link(use_only_title_matched_notes, use_only_title_matched_notes_expected):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_only_title_matched_notes)
    link_processor.match_link_title_to_notes(use_only_title_matched_notes)
    link_processor.match_renamed_links_using_link_ref_id()

    content = 'hello'

    result = link_processor.update_content(content)

    assert result == content


def test_update_content_use_only_title_matched_notes_content_with_valid_link_that_has_not_been_parsed(use_only_title_matched_notes, use_only_title_matched_notes_expected):
    link_processor = nsx_inter_note_link_processor.NSXInterNoteLinkProcessor()
    link_processor.make_list_of_links(use_only_title_matched_notes)
    link_processor.match_link_title_to_notes(use_only_title_matched_notes)
    link_processor.match_renamed_links_using_link_ref_id()

    content = 'hello'

    result = link_processor.update_content(content)

    assert result == content
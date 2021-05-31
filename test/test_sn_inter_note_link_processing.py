import pytest

import conversion_settings
import nsx_file_converter
import sn_inter_note_link_processing
import sn_note_page


@pytest.fixture
def conv_setting():
    conv_setting = conversion_settings.ConversionSettings()
    return conv_setting


@pytest.fixture
def nsx(conv_setting):
    nsx = nsx_file_converter.NSXFile('fake_file', conv_setting, 'fake_pandoc_converter')
    return nsx


@pytest.fixture
def all_note_pages(nsx):
    note_page_1_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_1 = sn_note_page.NotePage(nsx, 1, note_page_1_json)
    note_page_1.notebook_folder_name = 'note_book1'
    note_page_1._file_name = 'page-1-title.md'

    note_page_2_json = {'parent_id': 'note_book1', 'title': 'Page 2 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_2 = sn_note_page.NotePage(nsx, 1, note_page_2_json)
    note_page_2.notebook_folder_name = 'note_book1'
    note_page_2._file_name = 'page-2-title.md'

    note_page_3_json = {'parent_id': 'note_book1', 'title': 'Duplicate page title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_3 = sn_note_page.NotePage(nsx, 1, note_page_3_json)
    note_page_3.notebook_folder_name = 'note_book1'
    note_page_3._file_name = 'duplicate-page-title.md'

    note_page_4_json = {'parent_id': 'note_book1', 'title': 'Duplicate page title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_4 = sn_note_page.NotePage(nsx, 1, note_page_4_json)
    note_page_4.notebook_folder_name = 'note_book1'
    note_page_4._file_name = 'duplicate-page-title-1.md'

    note_page_5_json = {'parent_id': 'note_book2', 'title': 'Page 5 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_5 = sn_note_page.NotePage(nsx, 1, note_page_5_json)
    note_page_5.notebook_folder_name = 'note_book2'
    note_page_5._file_name = 'page-5-title.md'

    note_page_6_json = {'parent_id': 'note_book6', 'title': 'Duplicate page title across notebooks', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_6 = sn_note_page.NotePage(nsx, 1, note_page_6_json)
    note_page_6.notebook_folder_name = 'note_book1'
    note_page_6._file_name = 'duplicate-page-title2.md'

    note_page_7_json = {'parent_id': 'note_book6', 'title': 'Duplicate page title across notebooks', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    note_page_7 = sn_note_page.NotePage(nsx, 1, note_page_7_json)
    note_page_7.notebook_folder_name = 'note_book2'
    note_page_7._file_name = 'duplicate-page-title2-1.md'

    return [nsx_file_converter.Note('Page 1 title', note_page_1),
            nsx_file_converter.Note('Page 2 title', note_page_2),
            nsx_file_converter.Note('Duplicate page title', note_page_3),
            nsx_file_converter.Note('Duplicate page title', note_page_4),
            nsx_file_converter.Note('Page 5 title', note_page_5),
            nsx_file_converter.Note('Duplicate page title across notebooks', note_page_6),
            nsx_file_converter.Note('Duplicate page title across notebooks', note_page_7)
            ]

@pytest.fixture
def content():
    return """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">test page 2</a></div>"""


def test_process_inter_note_links_no_links_in_content(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div>"""

    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == content

def test_process_inter_note_links_no_matching_notes_exmaple_of_a_renamed_link_with_no_other_links_to_use_to_estimate_link(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/1234-1\">test page 2</a></div>"""

    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == content


def test_process_inter_note_links_no_matching_notes_exmaple_of_single_good_link(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 title</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href="page-1-title.md">Page 1 title</a></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected


def test_process_inter_note_links_no_matching_notes_exmaple_of_single_good_link_and_link_to_note_in_other_notebook(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 title</a></div><div>Below is a link to page 5 in a different notebook</div><div><a href=\"notestation://remote/self/1234-5\">Page 5 title</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href="page-1-title.md">Page 1 title</a></div><div>Below is a link to page 5 in a different notebook</div><div><a href="../note_book2/page-5-title.md">Page 5 title</a></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected


def test_process_inter_note_links_no_matching_notes_exmaple_of_single_good_link_and_link_to_note_in_other_notebook_and_a_reanmed_link_in_current_notebook(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 title</a></div><div>Below is a link to page 5 in a different notebook</div><div><a href=\"notestation://remote/self/1234-5\">Page 5 title</a></div><div>Below is a renamed link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 renamed</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href="page-1-title.md">Page 1 title</a></div><div>Below is a link to page 5 in a different notebook</div><div><a href="../note_book2/page-5-title.md">Page 5 title</a></div><div>Below is a renamed link to page 1</div><div><a href="page-1-title.md">Page 1 renamed</a></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected


def test_process_inter_note_links_no_matching_notes_exmaple_of_single_good_link_and_link_to_note_in_other_notebook_and_a_reanmed_link_in_different_notebook(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 title</a></div><div>Below is a link to page 5 in a different notebook</div><div><a href=\"notestation://remote/self/1234-5\">Page 5 title</a></div><div>Below is a renamed link to page 5</div><div><a href=\"notestation://remote/self/1234-5\">Page 5 renamed</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href="page-1-title.md">Page 1 title</a></div><div>Below is a link to page 5 in a different notebook</div><div><a href="../note_book2/page-5-title.md">Page 5 title</a></div><div>Below is a renamed link to page 5</div><div><a href="../note_book2/page-5-title.md">Page 5 renamed</a></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected

def test_process_inter_note_links_no_matching_notes_exmaple_of_single_good_link_and_link_to_note_in_other_notebook_and_a_reanmed_link_in_different_notebook_where_no_good_link_to_other_notebook_has_been_made(all_note_pages, nsx):
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href=\"notestation://remote/self/1234-1\">Page 1 title</a></div><div>Below is a renamed link to page 5</div><div><a href=\"notestation://remote/self/1234-5\">Page 5 renamed</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to page 1</div><div><a href="page-1-title.md">Page 1 title</a></div><div>Below is a renamed link to page 5</div><div><a href="notestation://remote/self/1234-5">Page 5 renamed</a></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected


def test_process_inter_note_links_duplicate_titles_in_same_workbook(all_note_pages, nsx):
    # expectation is to have two links - one to each note with he duplicated titles as it is not possible to know which one is being linked to
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to Duplicate page in notebook 1</div><div><a href=\"notestation://remote/self/1234-3\">Duplicate page title</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to Duplicate page in notebook 1</div><div><a href="duplicate-page-title.md">Duplicate page title</a><br><a href="duplicate-page-title-1.md">Duplicate page title</a><br></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected


def test_process_inter_note_links_duplicate_titles_in_same_workbook_both_linked_on_page(all_note_pages, nsx):
    # expectation is both links are replaced with two links - one to each duplicate file, so 4 new links in total
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to Duplicate page in notebook 1</div><div><a href=\"notestation://remote/self/1234-3\">Duplicate page title</a></div><div>Below is a link to the second Duplicate page in notebook 1</div><div><a href=\"notestation://remote/self/1234-4\">Duplicate page title</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to Duplicate page in notebook 1</div><div><a href="duplicate-page-title.md">Duplicate page title</a><br><a href="duplicate-page-title-1.md">Duplicate page title</a><br></div><div>Below is a link to the second Duplicate page in notebook 1</div><div><a href="duplicate-page-title.md">Duplicate page title</a><br><a href="duplicate-page-title-1.md">Duplicate page title</a><br></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected


def test_process_inter_note_links_duplicate_titles_in_different_workbooks(all_note_pages, nsx):
    # expectation is that each duplicated link recieves a list of posible duplicate links - so 2 duplicates will receive 4 links in total
    this_note_json = {'parent_id': 'note_book1', 'title': 'Page 1 title', 'mtime': 1619298559, 'ctime': 1619298539, 'attachment': {}, 'content': 'content', 'tag': []}
    this_note = sn_note_page.NotePage(nsx, 1, this_note_json)
    content = """<div>Below is a hyperlink to the internet</div><div><a href=\"https://github.com/kevindurston21/YANOM-Note-O-Matic\">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to Duplicate page title across notebooks notebook 1</div><div><a href=\"notestation://remote/self/1234-6\">Duplicate page title across notebooks</a></div><div>Below is a link to Duplicate page title across notebooks notebook 2</div><div><a href=\"notestation://remote/self/1234-7\">Duplicate page title across notebooks</a></div>"""
    expected = """<div>Below is a hyperlink to the internet</div><div><a href="https://github.com/kevindurston21/YANOM-Note-O-Matic">https://github.com/kevindurston21/YANOM-Note-O-Matic</a></div><div>Below is a link to Duplicate page title across notebooks notebook 1</div><div><a href="../note_book1/duplicate-page-title2.md">Duplicate page title across notebooks</a><br><a href="../note_book2/duplicate-page-title2-1.md">Duplicate page title across notebooks</a><br></div><div>Below is a link to Duplicate page title across notebooks notebook 2</div><div><a href="../note_book1/duplicate-page-title2.md">Duplicate page title across notebooks</a><br><a href="../note_book2/duplicate-page-title2-1.md">Duplicate page title across notebooks</a><br></div>"""
    link_processor = sn_inter_note_link_processing.SNLinksToOtherNotes(this_note, content, all_note_pages )

    link_processor.process_inter_note_links()

    assert isinstance(link_processor, sn_inter_note_link_processing.SNLinksToOtherNotes)

    assert link_processor.content == expected

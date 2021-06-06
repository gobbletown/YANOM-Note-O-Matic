from bs4 import BeautifulSoup
import pytest

import checklist_processing


def test_checklist_processing_html_to_md_good_html_check_pre_processing():
    html = """<p><input checked="" type="checkbox"/>Check 1</p><p><input type="checkbox"/>Check 2</p><p style="padding-left: 30px;"><input type="checkbox"/>Sub check 1</p><p style="padding-left: 30px;"><input checked="" type="checkbox"/>Sub check 2</p><p style="padding-left: 60px;"><input type="checkbox"/>Sub sub check 1</p><p style="padding-left: 60px;"><input checked="" type="checkbox"/>Sub sub check 2</p><p><input type="checkbox"/>Check 3</p>"""
    checklist_processor = checklist_processing.HTMLInputMDOutputChecklistProcessor(html)

    assert checklist_processor.processed_html.count("checklist-placeholder-id-") == 7


def test_checklist_processing_html_to_md_with_bad_nsx_html_check_pre_processing():
    html = """<div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub Check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div"""
    checklist_processor = checklist_processing.HTMLInputMDOutputChecklistProcessor(html)

    assert checklist_processor.processed_html.count("checklist-placeholder-id-") == 0


def test_checklist_processing_nsx_to_md_with_clean_html_check_pre_processing():
    html = """<p><input checked="" type="checkbox"/>Check 1</p><p><input type="checkbox"/>Check 2</p><p style="padding-left: 30px;"><input type="checkbox"/>Sub check 1</p><p style="padding-left: 30px;"><input checked="" type="checkbox"/>Sub check 2</p><p style="padding-left: 60px;"><input type="checkbox"/>Sub sub check 1</p><p style="padding-left: 60px;"><input checked="" type="checkbox"/>Sub sub check 2</p><p><input type="checkbox"/>Check 3</p>"""
    checklist_processor = checklist_processing.NSXInputMDOutputChecklistProcessor(html)

    assert checklist_processor.processed_html.count("checklist-placeholder-id-") == 0


def test_checklist_processing_nsx_to_md_with_nsx_html_check_pre_processing():
    html = """<div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub Check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div"""
    checklist_processor = checklist_processing.NSXInputMDOutputChecklistProcessor(html)

    assert checklist_processor.processed_html.count("checklist-placeholder-id-") == 5


@pytest.mark.parametrize(
    'html, expected', [
        ('<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>',
         '- [x] Check 1\n- [ ] Check 2\n\t- [ ] Sub check 1\n\t- [x] Sub check 2\n\t\t- [ ] Sub sub check 1\n\t\t- [x] Sub sub check 2\n- [ ] Check 3\n'),
        ('<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>',
         '- [x] Check 1\n- [ ] Check 2\n\t\t- [ ] Sub check 1\n\t- [x] Sub check 2\n\t\t- [ ] Sub sub check 1\n\t\t- [x] Sub sub check 2\n- [ ] Check 3\n'),
        ('<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>',
         '- [x] Check 1\n- [ ] Check 2\n\t- [ ] Sub check 1\n\t- [x] Sub check 2\n\t\t- [ ] Sub sub check 1\n\t\t- [x] Sub sub check 2\n- [ ] Check 3\n'),
        ('<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 45px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>',
         '- [x] Check 1\n- [ ] Check 2\n\t\t- [ ] Sub check 1\n\t- [x] Sub check 2\n\t\t\t- [ ] Sub sub check 1\n\t\t\t- [x] Sub sub check 2\n- [ ] Check 3\n'),
        ('<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 90px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>',
         '- [x] Check 1\n- [ ] Check 2\n\t- [ ] Sub check 1\n\t\t\t- [x] Sub check 2\n\t\t- [ ] Sub sub check 1\n\t\t- [x] Sub sub check 2\n- [ ] Check 3\n'),

        ]
)
def test_checklist_processing_nsx_to_md_with_nsx_html_markdown_output_check_post_processing(html, expected):
    checklist_processor = checklist_processing.NSXInputMDOutputChecklistProcessor(html)

    result = checklist_processor.add_checklist_items_to(checklist_processor.processed_html)

    assert result == expected

@pytest.mark.parametrize(
    'html, expected', [
        ('<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>',
         '<div><input checked="" type="checkbox"/>Check 1</div><div><input type="checkbox"/>Check 2</div><div style="padding-left: 30px;"><input type="checkbox"/>Sub check 1</div><div style="padding-left: 30px;"><input checked="" type="checkbox"/>Sub check 2</div><div style="padding-left: 60px;"><input type="checkbox"/>Sub sub check 1</div><div style="padding-left: 60px;"><input checked="" type="checkbox"/>Sub sub check 2</div><div><input type="checkbox"/>Check 3</div>'),
        ]
)
def test_checklist_processing_nsx_to_html_with_nsx_html_check_pre_processing(html, expected):
    checklist_processor = checklist_processing.NSXInputHTMLOutputChecklistProcessor(html)

    assert checklist_processor.processed_html == expected


def test_checklist_processing_nsx_to_html_with_nsx_html_html_output_check_post_processing():
    html = '<div><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 1</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 2</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 1</div><div style=\"padding-left: 30px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub check 2</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 1</div><div style=\"padding-left: 60px;\"><input class=\"syno-notestation-editor-checkbox syno-notestation-editor-checkbox-checked\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Sub sub check 2</div><div><input class=\"syno-notestation-editor-checkbox\" src=\"webman/3rdparty/NoteStation/images/transparent.gif\" type=\"image\" />Check 3</div>'
    checklist_processor = checklist_processing.NSXInputHTMLOutputChecklistProcessor(html)
    expected = checklist_processor.processed_html
    result = checklist_processor.add_checklist_items_to(checklist_processor.processed_html)

    assert result == expected  # confirm no changes made in post processing


@pytest.mark.parametrize(
    'html, expected_indent, expected_text', [
        ('<div><input type="checkbox"/>Check 1</div><div><input type="checkbox"/>Check 1</div>',
         0, 'Check 1'),
        ('<div><input type="checkbox"/>Check 1</div><div style=\"padding-left: 30px;\"><input type="checkbox"/>sub check 1</div>',
         1, 'sub check 1'),
        ('<div><input type="checkbox"/>Check 1</div><div style=\"padding-right: 30px;\"><input type="checkbox"/>sub check 1</div>',
         0, 'sub check 1'),
        ], ids=['no-indents', 'one-indent', 'invalid-indent-style']
)
def test_find_indent(html, expected_indent, expected_text):
    soup = BeautifulSoup(html)
    tag = soup.select('input[type="checkbox"]')
    checklist_processor = checklist_processing.HTMLInputMDOutputChecklistProcessor(html)

    assert checklist_processor.list_of_checklist_items[1].indent == expected_indent

    assert checklist_processor.list_of_checklist_items[1].text == expected_text




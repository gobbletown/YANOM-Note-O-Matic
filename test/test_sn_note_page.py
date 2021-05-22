# import pytest
#
# import sn_note_page
# import conversion_settings
# import nsx_file_converter
# import pandoc_converter
#
# def test_append_file_extension():
#     settings = conversion_settings.ConversionSettings()
#     settings.export_format = 'html'
#     settings.set_quick_setting('manual')
#     pandoc = pandoc_converter.PandocConverter(settings)
#     nsx_file = nsx_file_converter.NSXFile('file', settings, pandoc)
#     note_json = {'title': "My Note", 'content': "Hello world", 'parent_id': "1234", 'attachment': ''}
#     note = sn_note_page.NotePage(nsx_file, "1234", note_json)
#     result = note.append_file_extension()
#
#     assert 'My Note.html' == result

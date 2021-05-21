import pytest

import sn_note_page
import conversion_settings
import nsx_file_converter
import pandoc_converter



def test_append_file_extension():
    settings = conversion_settings.ManualConversionSettings()
    pandoc = pandoc_converter.PandocConverter(settings)
    nsx_file = nsx_file_converter.NSXFile('file', settings, pandoc)
    note = sn_note_page.NotePage(nsx_file, "1234")
    export_format = 'html'
    title = 'My Note'
    result = note.__append_file_extension(export_format, title)

    assert 'My Note.html' == result

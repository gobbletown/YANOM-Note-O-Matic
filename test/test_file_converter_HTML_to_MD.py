import unittest
import src.conversion_settings as quick_settings
from src.file_converter_HTML_to_MD import HTMLToMDConverter
from pathlib import Path
from src.metadata_processing import MetaDataProcessor


class TestHTMLToMDConverter(unittest.TestCase):

    def setUp(self):
        self.conversion_settings = quick_settings.please.provide('gfm')
        files_to_convert = [Path('not_existing.md'),
                            Path('some_markdown-old-1.md'),
                            Path('renaming source file failed'),
                            Path('test_html_file.md')]
        self.file_converter = HTMLToMDConverter(self.conversion_settings, files_to_convert)
        self.file_converter._metadata_processor = MetaDataProcessor(self.conversion_settings)

    def test_pre_process_content(self):
        self.file_converter._file_content = '<head><meta title="this is test2"/><meta not_valid="not_in_schema"/></head><p><input checked="" type="checkbox"/>Check 1</p><p><input type="checkbox"/>Check 2</p><p><a href="/a_folder/test_html_file.html">html file</a></p>'
        self.file_converter._metadata_schema = ['title']
        self.file_converter.pre_process_content()
        self.assertTrue('checklist-placeholder-id' in self.file_converter._pre_processed_content, 'Failed to insert checklist placeholders')
        self.assertTrue('<p><a href="/a_folder/test_html_file.md">html file</a></p>' in self.file_converter._pre_processed_content, 'Failed to change link extension placeholders')
        self.assertTrue({'title': 'this is test2'} == self.file_converter._metadata_processor.metadata, 'Failed to parse meta data')

    def test_post_process_content(self):
        self.file_converter._file_content = '<head><meta title="this is test2"/><meta not_valid="not_in_schema"/></head><p><input checked="" type="checkbox"/>Check 1</p><p><input type="checkbox"/>Check 2</p><img src="filepath/image.png" width="600">'
        self.file_converter._metadata_schema = ['title']
        self.file_converter._conversion_settings.export_format = 'pandoc_markdown'
        self.file_converter.pre_process_content()
        self.file_converter.convert_content()
        self.file_converter.post_process_content()
        self.assertEqual('- [x] Check 1\n- [ ] Check 2\n<img src="filepath/image.png" width="600" />\n\n', self.file_converter._post_processed_content, 'post processing failed')

        self.file_converter._file_content = '<head><meta title="this is test2"/><meta not_valid="not_in_schema"/></head><p><input checked="" type="checkbox"/>Check 1</p><p><input type="checkbox"/>Check 2</p><img src="filepath/image.png" width="600">'
        self.file_converter._metadata_schema = ['title']
        self.file_converter._conversion_settings.export_format = 'obsidian'
        self.file_converter.pre_process_content()
        self.file_converter.convert_content()
        self.file_converter.post_process_content()
        self.assertEqual('---\ntitle: this is test2\n---\n\n- [x] Check 1\n- [ ] Check 2\n![|600](filepath/image.png)\n', self.file_converter._post_processed_content, 'post processing failed')

    def test_parse_metadata_if_required(self):
        self.file_converter._conversion_settings.export_format = 'obsidian'
        self.file_converter._metadata_processor._metadata = {}
        self.file_converter._metadata_processor._metadata_schema = ['title', 'creation_time']
        self.file_converter._pre_processed_content = '<head><meta title="this is test2"/><meta creation_time="test-meta-content"/></head>'
        self.file_converter.parse_metadata_if_required()
        self.assertEqual({'title': 'this is test2'}, self.file_converter._metadata_processor.metadata, 'meta data not parsed correctly')

        self.file_converter._metadata_processor._metadata = {}
        self.file_converter._metadata_processor._metadata_schema = ['title']
        self.file_converter._pre_processed_content = '<meta title="this is test2"/><meta creation_time="test-meta-content"/>'
        self.file_converter.parse_metadata_if_required()
        self.assertEqual({}, self.file_converter._metadata_processor.metadata, 'meta data not ignored if no head section')

        self.file_converter._metadata_processor._metadata = {}
        self.file_converter._metadata_processor._metadata_schema = ['title']
        self.file_converter._pre_processed_content = '<head><meta title="this is test2"/><meta not_valid="not_in_schema"/></head>'
        self.file_converter.parse_metadata_if_required()
        self.assertEqual({'title': 'this is test2'},
                         self.file_converter._metadata_processor.metadata, 'meta data not parsed correctly')

        self.file_converter._conversion_settings.export_format = 'pandoc_markdown'
        self.file_converter._metadata_processor._metadata = {}
        self.file_converter._metadata_processor._metadata_schema = ['title', 'creation_time']
        self.file_converter._pre_processed_content = '<head><meta title="this is test2"/><meta creation_time="test-meta-content"/></head>'
        self.file_converter.parse_metadata_if_required()
        self.assertEqual({}, self.file_converter._metadata_processor.metadata, 'meta data not parsed correctly')

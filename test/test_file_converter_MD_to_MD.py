import unittest
import src.quick_settings as quick_settings
from src.file_converter_MD_to_MD import MDToMDConverter
from pathlib import Path
from testfixtures import TempDirectory
from src.metadata_processing import MetaDataProcessor


class TestMDToMDConverter(unittest.TestCase):

    def setUp(self):
        self.conversion_settings = quick_settings.please.provide('gfm')
        files_to_convert = [Path('not_existing.md'),
                            Path('some_markdown-old-1.md'),
                            Path('renaming source file failed')]
        self.file_converter = MDToMDConverter(self.conversion_settings, files_to_convert)
        self.file_converter._metadata_processor = MetaDataProcessor(self.conversion_settings)

    def test_add_meta_data_if_required(self):
        test_data_sets = [
            ('Hello',
             {},
             'gfm',
             'Hello',
             'no meta data, content was incorrect'
             ),
            ('Hello',
             {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
             'gfm',
             '---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             'good meta string and content failed'
             ),
            ('Hello',
             {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
             'markdown',
             'Hello',
             'good meta string and content failed'
             )
        ]

        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing {test_set}'):
                self.file_converter._post_processed_content = test_set[0]
                self.file_converter._metadata_processor._metadata = test_set[1]
                self.file_converter._conversion_settings.markdown_conversion_input = test_set[2]
                self.file_converter.add_meta_data_if_required()
                self.assertEqual(test_set[3],
                                 self.file_converter._post_processed_content,
                                 test_set[4])

    def test_parse_metadata_if_required(self):
        test_data_sets = [
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             'gfm',
             {'title': 'Hello, world!'},
             'good meta string failed',
             'Hello',
             'good meta string failed'
             ),
            ('Hello',
             'gfm',
             {},
             'no meta string failed',
             'Hello',
             'no meta string failed'
             ),
            ('---\nthis :is:nonsense\nmore\nnonsense\n---\n\nHello',
             'gfm',
             {},
             'bad meta data failed',
             'Hello',
             'bad meta data failed'
             ),
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             'markdown',
             {},
             'good meta string failed',
             '---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             'good meta string failed'
             )
        ]
        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing {test_set}'):
                self.file_converter._pre_processed_content = test_set[0]
                self.file_converter._conversion_settings.markdown_conversion_input = test_set[1]
                self.file_converter.parse_metadata_if_required()
                self.assertEqual(test_set[2], self.file_converter._metadata_processor.metadata, test_set[3])
                self.assertEqual(test_set[4], self.file_converter._pre_processed_content, test_set[5])

    def test_rename_target_file_if_already_exists(self):
        test_strings = [
            ('some_markdown.md',
             'not_existing.md',
             'some_markdown-old-1.md',
             'renaming source file failed'),
            ('some_markdown.md',
             'some_markdown-old-1.md',
             'some_markdown-old-2.md',
             'renaming for existing old file failed'),
        ]
        for test_set in test_strings:
            with self.subTest(msg=f'Testing when existing old set to {test_set[0]}'):
                with TempDirectory() as d:
                    source_file = Path(d.path, test_set[0])
                    source_file.touch()
                    source_file_old_exists = Path(d.path, test_set[1])
                    source_file_old_exists.touch()
                    self.assertTrue(source_file.exists())
                    self.assertTrue(source_file_old_exists.exists())

                    self.file_converter._file = source_file
                    self.file_converter.rename_target_file_if_already_exists()
                    self.assertTrue(Path(d.path, test_set[2]).exists(), test_set[3])

        with TempDirectory() as d:
            self.file_converter._file = Path('does_not_exist.md')
            self.file_converter.rename_target_file_if_already_exists()
            self.assertFalse(Path(d.path, 'does_not_exist.md').exists(), 'failed to manage a not existing file name')
            self.assertFalse(Path(d.path, 'does_not_exist-old.md').exists(), 'failed to manage a not existing file name')
            self.assertFalse(Path(d.path, 'does_not_exist-old-1.md').exists(), 'failed to manage a not existing file name')


    def test_pre_process_obsidian_image_links_if_required(self):
        test_strings = [
            ('obsidian',
             '![|600](filepath/image.png)',
             '<img src="filepath/image.png" width="600">',
             'obsidian link to gfm failed'),
            ('obsidian',
             '![](filepath/image.png)',
             '![](filepath/image.png)',
             'markdown std link not left unchanged'),
            ('obsidian',
             '![|some-text](filepath/image.png)',
             '![|some-text](filepath/image.png)',
             'markdown std with pipe and text link not left unchanged',),
            ('commonmark',
             '![](filepath/image.png)',
             '![](filepath/image.png)',
             'non obsidian input image incorrectly changed')
        ]

        for test_set in test_strings:
            with self.subTest(msg=f'Testing image link format {test_set[1]} conversion'):
                self.conversion_settings.markdown_conversion_input = test_set[0]
                self.file_converter._pre_processed_content = test_set[1]
                self.file_converter.pre_process_obsidian_image_links_if_required()
                self.assertEqual(test_set[2],
                                 self.file_converter._pre_processed_content,
                                 test_set[3])

    def test_pre_process_content(self):
        test_strings = [
            ('obsidian',
             '![|600](filepath/image.png)',
             '<img src="filepath/image.png" width="600">',
             'obsidian link to gfm failed'),
            ('obsidian',
             '![](filepath/image.png)',
             '![](filepath/image.png)',
             'markdown std link not left unchanged'),
            ('obsidian',
             '![|some-text](filepath/image.png)',
             '![|some-text](filepath/image.png)',
             'markdown std with pipe and text link not left unchanged',),
            ('commonmark',
             '![](filepath/image.png)',
             '![](filepath/image.png)',
             'non obsidian input image incorrectly changed')
        ]

        for test_set in test_strings:
            with self.subTest(msg=f'Testing image link format {test_set[1]} conversion'):
                with TempDirectory() as d:
                    source_file = Path(d.path, 'some_markdown.md')
                    source_file.touch()
                    self.assertTrue(source_file.exists())
                    self.file_converter._file = source_file

                    self.conversion_settings.markdown_conversion_input = test_set[0]
                    self.file_converter._file_content = test_set[1]
                    self.file_converter.pre_process_content()
                    self.assertEqual(test_set[2],
                                     self.file_converter._pre_processed_content,
                                     test_set[3])

    def test_post_process_obsidian_image_links_if_required(self):
        test_strings = [
            ('<img src="filepath/image.png" width="600">',
             '![|600](filepath/image.png)',
             'link not converted to obsidian correctly'
             ),
            ('<img src="filepath/image.png" width="600"/>',
             '![|600](filepath/image.png)',
             'link with closing forward slash not converted to obsidian correctly'
             ),
            ('![](filepath/image.png)',
             '![](filepath/image.png)',
             'std markdown image link not left alone'
             )
        ]
        self.conversion_settings.export_format = 'obsidian'

        for test_set in test_strings:
            with self.subTest(msg=f'Testing image link format {test_set[0]} conversion'):
                self.file_converter._post_processed_content = test_set[0]
                self.file_converter.post_process_obsidian_image_links_if_required()
                self.assertEqual(test_set[1],
                                 self.file_converter._post_processed_content,
                                 test_set[2])

    def test_read_file(self):
        with TempDirectory() as d:
            source_file = Path(d.path, 'some_markdown.md')
            source_file.write_text('hello\nworld!')
            self.file_converter._file = source_file

            self.file_converter.read_file()
            self.assertEqual('hello\nworld!', self.file_converter._file_content, 'failed to read file content')

    def test_convert_content(self):
        self.file_converter._pre_processed_content = '<h1>Header 1</h1>'
        self.file_converter.convert_content()
        self.assertEqual('# Header 1\n', self.file_converter._converted_content, 'failed to convert content')

    def test_write_post_processed_content(self):
        with TempDirectory() as d:
            self.file_converter._file = Path(d.path, 'test.txt')
            self.file_converter._post_processed_content = '# Header 1\n'
            self.file_converter.write_post_processed_content()
            output_path = Path(d.path, 'test.md')
            read_text = output_path.read_text()
            self.assertEqual('# Header 1\n', read_text, 'Failed to write content')

    def test_post_process_content(self):
        self.file_converter._pre_processed_content = 'Hello'
        self.file_converter._metadata_processor._metadata = {'test': 'data'}
        self.file_converter._conversion_settings.markdown_conversion_input = 'gfm'
        self.file_converter.post_process_content()

        self.assertEqual('---\ntest: data\n---\n\nHello',
                         self.file_converter._post_processed_content,
                         'failed to post process content')

        self.file_converter._pre_processed_content = '---\ntest: data\n---\n\nHello'
        self.file_converter._metadata_processor._metadata = {'tile': 'My Title'}
        self.file_converter._conversion_settings.markdown_conversion_input = 'markdown'
        self.file_converter.post_process_content()

        self.assertEqual('---\ntest: data\n---\n\nHello',
                         self.file_converter._post_processed_content,
                         'failed to post process content')

        self.file_converter._pre_processed_content = '---\ntest: data\n---\n\nHello'
        self.file_converter._metadata_processor._metadata = {'title': 'My Title'}
        self.file_converter._conversion_settings.markdown_conversion_input = 'gfm'
        self.file_converter.post_process_content()

        self.assertEqual('---\ntitle: My Title\n---\n\n---\ntest: data\n---\n\nHello',
                         self.file_converter._post_processed_content,
                         'failed to post process content')

    def test_set_out_put_extension(self):
        extension = self.file_converter.set_out_put_file_extension()
        self.assertEqual('.md', extension, 'failed to select correct md extension')

        self.file_converter._conversion_settings = quick_settings.please.provide('html')
        extension = self.file_converter.set_out_put_file_extension()
        self.assertEqual('.html', extension, 'failed to select correct html extension')

    def test_convert(self):
        self.file_converter._conversion_settings = quick_settings.please.provide('obsidian')
        with TempDirectory() as d:
            source_file = Path(d.path, 'some_markdown.md')
            source_file.write_text('<img src="filepath/image.png" width="600">')
            self.file_converter.convert(source_file)

            result = source_file.read_text()
            self.assertEqual('![|600](filepath/image.png)', result, 'failed to convert file')

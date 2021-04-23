import unittest
import src.conversion_settings as quick_settings
from src.file_converter_MD_to_HTML import MDToHTMLConverter
from pathlib import Path
from testfixtures import TempDirectory
from src.metadata_processing import MetaDataProcessor


class TestMDToHTMLConverter(unittest.TestCase):
    def setUp(self):
        self.conversion_settings = quick_settings.please.provide('gfm')
        files_to_convert = [Path('not_existing.md'),
                            Path('some_markdown-old-1.md'),
                            Path('renaming source file failed'),
                            Path('a_folder/test_md_file.md')]
        self.file_converter = MDToHTMLConverter(self.conversion_settings, files_to_convert)
        self.file_converter._metadata_processor = MetaDataProcessor(self.conversion_settings)

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

        test_strings = [
            ('markdown',
             '---\nexcerpt: tl;dr\nlayout: post\ntitle: TITLE\n---\n\n# Hello',
             '---\nexcerpt: tl;dr\nlayout: post\ntitle: TITLE\n---\n\n# Hello',
             'markdown pre processing for meta data failed'),
            ('gfm',
             '---\nexcerpt: tl;dr\nlayout: post\ntitle: TITLE\n---\n\n# Hello',
             '# Hello',
             'non-markdown pre processing for meta data failed'),
        ]
        for test_set in test_strings:
            with self.subTest(msg='testing meta data handling'):
                with TempDirectory() as d:
                    source_file = Path(d.path, 'some_markdown.md')
                    source_file.touch()
                    self.assertTrue(source_file.exists())
                    self.file_converter._file = source_file

                    self.conversion_settings.markdown_conversion_input = test_set[0]
                    self.file_converter._file_content = test_set[1]
                    self.file_converter.pre_process_content()
                    self.assertEqual(test_set[2], self.file_converter._pre_processed_content, test_set[3])

    def test_change_md_links_to_html_links(self):
        self.file_converter._files_to_convert = [Path('not_existing.md'),
                                                 Path('some_markdown-old-1.md'),
                                                 Path('renaming source file failed'),
                                                 Path('a_folder/test_md_file.md'),
                                                 Path('a_folder/test_.md_file.md')]


        content = '<p><a href="a_folder/test_md_file.md">md file</a></p>' \
                  '<p><a href="a_folder/test_.md_file.md">md file  with dot md in name</a></p>' \
                  '<p><a href="a_folder/test_pdf_file.pdf">non md file file</a>' \
                  '</p><p><a href="https://a_folder/test_pdf_file.md">web md file</a></p>' \
                  '<p><a href="a_folder/not_in_convert_list.md">non md file file</a></p>'

        new_content = self.file_converter.update_note_links(content, 'md', 'html')

        print(content)
        print(new_content)
        self.assertTrue('<p><a href="a_folder/test_md_file.html">md file</a></p>' in new_content,
                        'clean md file extension not changed correctly')
        self.assertTrue('<p><a href="a_folder/test_.md_file.html">md file  with dot md in name</a></p>'
                        in new_content,
                        ' md file with dot md in name  not changed correctly')
        self.assertTrue('<p><a href="a_folder/test_pdf_file.pdf">non md file file</a></p>'
                        in new_content,
                        'non md file extension changed incorrectly')
        self.assertTrue('</p><p><a href="https://a_folder/test_pdf_file.md">web md file</a></p>'
                        in new_content,
                        'internet md file extension changed incorrectly')
        self.assertTrue('<p><a href="a_folder/not_in_convert_list.md">non md file file</a></p>'
                        in new_content,
                        'file with md file extension not in to be changed list changed incorrectly')

    #     def test_add_meta_data_if_required(self):
    #         self.file_converter._post_processed_content = '<title>-</title>'
    #         self.file_converter._meta_content = {'title': 'My Title'}
    #         self.file_converter.add_meta_data_if_required()
    #         self.assertEqual('<title>My Title</title><meta title="My Title"/>', self.file_converter._post_processed_content,
    #                          'title and meta data inserted incorrectly')
    #
    #         self.file_converter._post_processed_content = """<!DOCTYPE html>
    #
    # <html lang="" xml:lang="" xmlns="http://www.w3.org/1999/xhtml">
    # <head>
    # <meta charset="utf-8"/>
    # <meta content="pandoc" name="generator"/>
    # <meta content="width=device-width, initial-scale=1.0, user-scalable=yes" name="viewport"/>
    # <title>-</title>
    # <style>
    #     html {
    #       line-height: 1.5;
    #       font-family: Georgia, serif;
    #       font-size: 20px;
    #       color: #1a1a1a;
    #       background-color: #fdfdfd;
    #     }
    # </style>
    # </head></html>
    # """
    #         self.file_converter._meta_content = {'test': 'test-meta-content', 'test2': 'this is test2'}
    #
    #         expected_result = """<!DOCTYPE html>
    #
    # <html lang="" xml:lang="" xmlns="http://www.w3.org/1999/xhtml">
    # <head>
    # <meta charset="utf-8"/>
    # <meta content="pandoc" name="generator"/>
    # <meta content="width=device-width, initial-scale=1.0, user-scalable=yes" name="viewport"/>
    # <title>-</title><meta test2="this is test2"/><meta test="test-meta-content"/>
    # <style>
    #     html {
    #       line-height: 1.5;
    #       font-family: Georgia, serif;
    #       font-size: 20px;
    #       color: #1a1a1a;
    #       background-color: #fdfdfd;
    #     }
    # </style>
    # </head></html>
    # """
    #
    #         self.file_converter.add_meta_data_if_required()
    #
    #         self.assertEqual(expected_result, self.file_converter._post_processed_content, 'meta data inserted incorrectly')
    #
    #         self.file_converter._post_processed_content = '<title>-</title>'
    #         self.file_converter.add_meta_data_if_required()
    #         self.assertEqual('<title>-</title><meta test2="this is test2"/><meta test="test-meta-content"/>', self.file_converter._post_processed_content, 'meta data inserted incorrectly')
    #
    #         self.file_converter._post_processed_content = '<h1>hello</h1>'
    #         self.file_converter.add_meta_data_if_required()
    #         self.assertEqual('<h1>hello</h1>', self.file_converter._post_processed_content, 'meta data inserted incorrectly')
    #
    #         self.file_converter._post_processed_content = '<title>-</title>'
    #         self.file_converter._meta_content = {}
    #         self.file_converter.add_meta_data_if_required()
    #         self.assertEqual('<title>-</title>', self.file_converter._post_processed_content, 'meta data inserted incorrectly')
    #
    #         self.file_converter._conversion_settings.markdown_conversion_input = 'markdown'
    #         self.file_converter._post_processed_content = '<title>-</title>'
    #         self.file_converter.add_meta_data_if_required()
    #         self.assertEqual('<title>-</title>', self.file_converter._post_processed_content, 'meta data inserted incorrectly')

    def test_post_process_content(self):
        self.file_converter._conversion_settings.markdown_conversion_input = 'gfm'
        self.file_converter._converted_content = '<head><title>-</title></head><p><a href="a_folder/test_md_file.md">md file</a></p>'
        self.file_converter._metadata_processor._metadata = {'title': 'My Title'}
        self.file_converter.post_process_content()
        self.assertEqual(
            '<head><title>My Title</title><meta title="My Title"/></head><p><a href="a_folder/test_md_file.html">md file</a></p>',
            self.file_converter._post_processed_content,
            'title and meta data inserted incorrectly')

    def test_add_meta_data_if_required(self):
        self.file_converter._conversion_settings.markdown_conversion_input = 'gfm'
        self.file_converter._post_processed_content = '<head><title>-</title></head><p><a href="a_folder/test_md_file.md">md file</a></p>'
        self.file_converter._metadata_processor._metadata = {'title': 'My Title'}
        self.file_converter.add_meta_data_if_required()
        self.assertEqual(
            '<head><title>My Title</title><meta title="My Title"/></head><p><a href="a_folder/test_md_file.md">md file</a></p>',
            self.file_converter._post_processed_content,
            'title and meta data inserted incorrectly')

        self.file_converter._conversion_settings.markdown_conversion_input = 'pandoc_markdown'
        self.file_converter._post_processed_content = '<head><title>-</title></head><p><a href="a_folder/test_md_file.md">md file</a></p>'
        self.file_converter._metadata_processor._metadata = {'title': 'My Title'}
        self.file_converter.add_meta_data_if_required()
        self.assertEqual(
            '<head><title>-</title></head><p><a href="a_folder/test_md_file.md">md file</a></p>',
            self.file_converter._post_processed_content,
            'title and meta data inserted incorrectly with markdown conversion input')
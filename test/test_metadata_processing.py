import unittest

import pytest

from src.conversion_settings import ConversionSettings
from src.metadata_processing import MetaDataProcessor


class TestMetaDataProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.conversion_settings = ConversionSettings()
        self.conversion_settings.set_quick_setting('gfm')
        self.metadata_processor = MetaDataProcessor(self.conversion_settings)

    def test_remove_tag_spaces_if_required(self):
        test_data_sets = [
            ({'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/SubTag1",
                   "Tag1/SubTag1/SubSubTag1",
                   "Tag2"]
              },
             False,
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/SubTag1",
                   "Tag1/SubTag1/SubSubTag1",
                   "Tag2"]
              },
             'removing spaces failed when there were no spaces'
             ),
            ({'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub Tag1",
                   "Tag1/Sub Tag1/Sub Sub Tag1",
                   "Tag2"]
              },
             False,
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub-Tag1",
                   "Tag1/Sub-Tag1/Sub-Sub-Tag1",
                   "Tag2"]
              },
             'removing spaces failed when there were spaces'
             ),
            ({'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub Tag1",
                   "Tag1/Sub Tag1/Sub Sub Tag1",
                   "Tag2"]
              },
             True,
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub Tag1",
                   "Tag1/Sub Tag1/Sub Sub Tag1",
                   "Tag2"]
              },
             'removing spaces failed when NOT required'
             ),
        ]
        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing {test_set}'):
                self.metadata_processor._metadata = test_set[0]
                self.metadata_processor._spaces_in_tags = test_set[1]
                self.metadata_processor.remove_tag_spaces_if_required()

                self.assertEqual(test_set[2], self.metadata_processor.metadata, test_set[3])

    def test_split_tags_if_required(self):
        test_data_sets = [
            ({'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/SubTag1",
                   "Tag1/SubTag1/SubSubTag1",
                   "Tag2"]
              },
             True,
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "SubTag1",
                   "SubSubTag1",
                   "Tag2"]
              },
             'splitting tags with no spaces failed'
             ),
            ({'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub Tag1",
                   "Tag1/Sub Tag1/Sub Sub Tag1",
                   "Tag2"]
              },
             True,
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Sub Tag1",
                   "Sub Sub Tag1",
                   "Tag2"]
              },
             'splitting tags with spaces failed'
             ),
            ({'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub Tag1",
                   "Tag1/Sub Tag1/Sub Sub Tag1",
                   "Tag2"]
              },
             False,
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678',
              'tags':
                  ["Tag1",
                   "Tag1/Sub Tag1",
                   "Tag1/Sub Tag1/Sub Sub Tag1",
                   "Tag2"]
              },
             'splitting tags failed when NOT required'
             ),
        ]
        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing {test_set}'):
                self.metadata_processor._metadata = test_set[0]
                self.metadata_processor._split_tags = test_set[1]
                self.metadata_processor.split_tags_if_required()
                self.assertTrue(
                    sorted(test_set[2]['tags']) == sorted(self.metadata_processor.metadata['tags']),
                    test_set[3])

    def test_parse_dict_metadata(self):
        test_data_sets = [
            (['title', 'ctime', 'mtime'],
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678'
              },
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678'
              },
             'generating selected metadata failed for clean data'
             ),
            (['title', 'mtime'],
             {'title': 'My Title',
              'ctime': '1234',
              'mtime': '5678'
              },
             {'title': 'My Title',
              'mtime': '5678'
              },
             'generating metadata with one less item in schema failed'
             ),
            (['title', 'tags', 'ctime', 'mtime'],
             {'title': 'My Title',
              'ctime': '1234'
              },
             {'title': 'My Title',
              'ctime': '1234'
              },
             'generating selected metadata failed for meta data missing one of the schema keys'
             ),
            ([],
             {'title': 'My Title',
              'ctime': '1234'
              },
             {},
             'generating selected metadata failed for meta data missing a schema tag'
             ),
            (['title', 'tags', 'ctime', 'mtime'],
             {},
             {},
             'generating selected metadata failed for empty metadata'
             ),
        ]

        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing {test_set}'):
                self.metadata_processor._metadata = {}
                self.metadata_processor._metadata_schema = test_set[0]
                self.metadata_processor.parse_dict_metadata(test_set[1])
                self.assertTrue(test_set[2] == self.metadata_processor.metadata, test_set[3])

        self.metadata_processor._split_tags = True
        self.metadata_processor._spaces_in_tags = False
        self.metadata_processor._metadata = {}
        self.metadata_processor._metadata_schema = ['tags']
        raw_metadata = {'tags': ["Tag1",
                                 "Tag1/Sub Tag1",
                                 "Tag1/Sub Tag1/Sub Sub Tag1",
                                 "Tag2"]}
        expected_result = {'tags': ["Tag1",
                                    "Sub-Tag1",
                                    "Sub-Sub-Tag1",
                                    "Tag2"]}
        self.metadata_processor.parse_dict_metadata(raw_metadata)

        self.assertTrue(
            sorted(expected_result['tags']) == sorted(self.metadata_processor.metadata['tags']),
            'generating metadata with tags failed')

    def test_add_metadata_html_to_content(self):
        content = '<head><title>-</title></head>'
        self.metadata_processor._metadata = {'title': 'My Title'}
        new_content = self.metadata_processor.add_metadata_html_to_content(content)
        self.assertEqual('<head><title>My Title</title><meta title="My Title"/></head>',
                         new_content,
                         'title and meta data inserted incorrectly')

        content = """<!DOCTYPE html>

<html lang="" xml:lang="" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8"/>
<meta content="pandoc" name="generator"/>
<meta content="width=device-width, initial-scale=1.0, user-scalable=yes" name="viewport"/>
<title>-</title>
<style>
    html {
      line-height: 1.5;
      font-family: Georgia, serif;
      font-size: 20px;
      color: #1a1a1a;
      background-color: #fdfdfd;
    }
</style>
</head></html>
"""
        self.metadata_processor._metadata = {'test': 'test-meta-content', 'test2': 'this is test2'}

        expected_result = """<!DOCTYPE html>

<html lang="" xml:lang="" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8"/>
<meta content="pandoc" name="generator"/>
<meta content="width=device-width, initial-scale=1.0, user-scalable=yes" name="viewport"/>
<title>-</title>
<style>
    html {
      line-height: 1.5;
      font-family: Georgia, serif;
      font-size: 20px;
      color: #1a1a1a;
      background-color: #fdfdfd;
    }
</style>
<meta test="test-meta-content"/><meta test2="this is test2"/></head></html>
"""

        new_content = self.metadata_processor.add_metadata_html_to_content(content)

        self.assertEqual(expected_result, new_content, 'meta data inserted incorrectly')

        content = '<title>-</title>'
        self.metadata_processor._metadata = {'test': 'test-meta-content', 'test2': 'this is test2'}
        new_content = self.metadata_processor.add_metadata_html_to_content(content)
        self.assertEqual('<title>-</title>',
                         new_content, 'meta data inserted incorrectly when there is no head')

        content = '<head></head><h1>hello</h1>'
        self.metadata_processor._metadata = {'test': 'test-meta-content', 'test2': 'this is test2'}
        new_content = self.metadata_processor.add_metadata_html_to_content(content)
        self.assertEqual('<head><meta test="test-meta-content"/><meta test2="this is test2"/></head><h1>hello</h1>',
                         new_content, 'meta data inserted incorrectly')

        content = '<head></head><h1>hello</h1>'
        self.metadata_processor._metadata = {}
        new_content = self.metadata_processor.add_metadata_html_to_content(content)
        self.assertEqual('<head></head><h1>hello</h1>', new_content, 'meta data inserted incorrectly')

        content = '<title>-</title>'
        self.metadata_processor._metadata = {'test': 'test-meta-content', 'test2': 'this is test2'}
        new_content = self.metadata_processor.add_metadata_html_to_content(content)
        self.assertEqual('<title>-</title>', new_content, 'meta data inserted incorrectly')

        self.metadata_processor._conversion_settings.markdown_conversion_input = 'pandoc_markdown'
        content = '<head><title>-</title></head>'
        self.metadata_processor._metadata = {'test': 'test-meta-content', 'test2': 'this is test2'}
        new_content = self.metadata_processor.add_metadata_html_to_content(content)
        self.assertEqual('<head><title>-</title><meta test="test-meta-content"/><meta test2="this is test2"/></head>',
                         new_content, 'meta data inserted incorrectly')

    def test_parse_html_meta_data(self):
        test_data_sets = [
            (['title', 'creation_time'],
             '<head><meta title="this is test2"/><meta creation_time="test-meta-content"/></head>',
             {'title': 'this is test2', 'creation_time': 'test-meta-content'},
             'meta data not parsed correctly'),
            (['title', 'creation_time'],
             '<meta title="this is test2"/><meta creation_time="test-meta-content"/>',
             {},
             'meta data not ignored if no head section'),
            (['title', 'creation_time'],
             '<head><meta title="this is test2"/><meta not_valid="not_in_schema"/></head>',
             {'title': 'this is test2'},
             'meta data not parsed correctly when meta not in schema present'),
            ([],
             '<head><meta title="this is test2"/><meta not_valid="not_in_schema"/></head>',
             {},
             'meta data not parsed correctly when there is no schema')
        ]
        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing paring of html for meta tags {test_set}'):
                self.metadata_processor._metadata = {}
                self.metadata_processor._metadata_schema = test_set[0]
                self.metadata_processor.parse_html_metadata(test_set[1])
                self.assertEqual(test_set[2], self.metadata_processor.metadata, test_set[3])

    def test_format_tag_metadata_if_required(self):
        self.metadata_processor._split_tags = True
        self.metadata_processor._spaces_in_tags = False

        self.metadata_processor._metadata = {'tags': ["Tag1",
                                                      "Tag1/Sub Tag1",
                                                      "Tag1/Sub Tag1/Sub Sub Tag1",
                                                      "Tag2"]}
        self.metadata_processor.format_tag_metadata_if_required()
        self.assertEqual(sorted(["Tag1", "Sub-Tag1", "Sub-Sub-Tag1", "Tag2"]),
                         sorted(self.metadata_processor.metadata['tags']),
                         'formatting tags if required failed')

    def test_parse_md_metadata(self):
        test_data_sets = [
            ('Hello',
             ['title', 'tag', 'ctime', 'mtime'],
             'Hello',
             'no meta data, content was incorrect',
             {},
             'no meta data to parse, resulted in having metadata'
             ),
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             ['title', 'tag', 'ctime', 'mtime'],
             'Hello',
             'with md metadata, content was incorrect',
             {'title': 'Hello, world!'},
             'with md metadata to parse, incorrect metadata'
             ),
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             [''],
             'Hello',
             'with md metadata and empty schema, content was incorrect',
             {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
             'with md metadata and empty schema, incorrect metadata'
             ),
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             ['title', 'layout', 'ctime', 'mtime'],
             'Hello',
             'with md metadata, content was incorrect',
             {'title': 'Hello, world!', 'layout': 'post'},
             'with md metadata to parse, incorrect metadata'
             ),
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             ['ctime', 'mtime'],
             'Hello',
             'with md metadata and no vlaid matches in schema, content was incorrect',
             {},
             'with md metadata and no vlaid matches in schema, incorrect metadata'
             ),
            ('---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
             [],
             'Hello',
             'with md metadata and empty schema, content was incorrect',
             {},
             'with md metadata and empty schema, incorrect metadata'
             ),
        ]

        for test_set in test_data_sets:
            with self.subTest(msg=f'Testing parsing meta data form MD {test_set}'):
                md_string = test_set[0]
                self.metadata_processor._metadata = {}
                self.metadata_processor._metadata_schema = test_set[1]
                new_content = self.metadata_processor.parse_md_metadata(md_string)
                self.assertEqual(test_set[2], new_content, test_set[3])
                self.assertTrue(test_set[4] == self.metadata_processor.metadata, test_set[5])


def test_add_metadata_md_to_content(self):
    test_data_sets = [
        ('Hello',
         {},
         'Hello',
         'no meta data, content was incorrect'
         ),
        ('Hello',
         {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
         '---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
         'good meta string and content failed'
         )
    ]

    for test_set in test_data_sets:
        with self.subTest(msg=f'Testing adding meta data to MD {test_set}'):
            content = test_set[0]
            self.metadata_processor._metadata = test_set[1]
            new_content = self.metadata_processor.add_metadata_md_to_content(content)
            self.assertEqual(test_set[2], new_content, test_set[3])


@pytest.mark.parametrize(
    'md_string, markdown_conversion_input, expected', [
        (
        "---\nctime: '202102122352'\nmtime: '202104242208'\ntag:\n- Tag1\n- Tag1/SubTag1\n- Tag1/SubTag1/SubSubTag1\n- Tag2\ntitle: test page\n---\n\n# This is H1",
        'obsidian',
        'ctime: 202102122352\nmtime: 202104242208\ntag: #Tag1, #Tag1/SubTag1, #Tag1/SubTag1/SubSubTag1, #Tag2title: test page\n\nhello'),
        ("---\nctime: '202102122352'\nmtime: '202104242208'\ntag: \ntitle: test page\n---\n\n# This is H1",
         'obsidian',
         'ctime: 202102122352\nmtime: 202104242208\ntitle: test page\n\nhello'),
        ("# This is H1",
         'obsidian',
         "hello"),
        (
        "---\nctime: '202102122352'\nmtime: '202104242208'\ntag:\n- Tag1\n- Tag1/SubTag1\n- Tag1/SubTag1/SubSubTag1\n- Tag2\ntitle: test page\n---\n\n# This is H1",
        'pandoc_markdown_strict',
        'ctime: 202102122352\nmtime: 202104242208\ntag: #Tag1, #Tag1/SubTag1, #Tag1/SubTag1/SubSubTag1, #Tag2title: test page\n\nhello'),
    ]
)
def test_add_text_metadata_to_content(md_string, markdown_conversion_input, expected):
    conversion_settings = ConversionSettings()
    conversion_settings.markdown_conversion_input = markdown_conversion_input
    conversion_settings.metadata_schema = ['title', 'ctime', 'mtime', 'tag']
    metadata_processor = MetaDataProcessor(conversion_settings)
    metadata_processor.parse_md_metadata(md_string)
    content = "hello"

    result = metadata_processor.add_text_metadata_to_content(content)

    assert result == expected


@pytest.mark.parametrize(
    'md_string, expected', [
        (
        "---\nctime: '202102122352'\nmtime: '202104242208'\ntag:\n- Tag1\n- Tag1/SubTag1\n- Tag1/SubTag1/SubSubTag1\n- Tag2\ntitle: test page\n---\n\n# This is H1",
        {'ctime': '202102122352', 'mtime': '202104242208',
         'tag': ['#Tag1', '#Tag1/SubTag1', '#Tag1/SubTag1/SubSubTag1', '#Tag2'], 'title': 'test page'}),
        (
        "---\nctime: '202102122352'\nmtime: '202104242208'\ntags:\n- Tag1\n- Tag1/SubTag1\n- Tag1/SubTag1/SubSubTag1\n- Tag2\ntitle: test page\n---\n\n# This is H1",
        {'ctime': '202102122352', 'mtime': '202104242208',
         'tags': ['#Tag1', '#Tag1/SubTag1', '#Tag1/SubTag1/SubSubTag1', '#Tag2'], 'title': 'test page'}),
    ]
)
def test_add_tag_prefix_if_required(md_string, expected):
    conversion_settings = ConversionSettings()
    conversion_settings.tag_prefix = '#'
    conversion_settings.metadata_schema = ['']
    metadata_processor = MetaDataProcessor(conversion_settings)

    # md_string = "---\nctime: '202102122352'\nmtime: '202104242208'\ntag:\n- Tag1\n- Tag1/SubTag1\n- Tag1/SubTag1/SubSubTag1\n- Tag2\ntitle: test page\n---\n\n# This is H1"
    # expected = {'ctime': '202102122352', 'mtime': '202104242208', 'tag': ['#Tag1', '#Tag1/SubTag1', '#Tag1/SubTag1/SubSubTag1', '#Tag2'], 'title': 'test page'}

    metadata_processor.parse_md_metadata(md_string)

    metadata_processor.add_tag_prefix_if_required()

    assert metadata_processor.metadata == expected


@pytest.mark.parametrize(
    'html_string, expected, schema', [
        (
        '<head><title>test page</title><meta title="test page"/><meta ctime="202102122352"/><meta mtime="202104242208"/><meta tag="Tag1,Tag1/SubTag1,Tag1/SubTag1/SubSubTag1,Tag2"/></head><h1>This is H1</h1',
        {'ctime': '202102122352', 'mtime': '202104242208',
         'tag': ['Tag1', 'Tag1/SubTag1', 'Tag1/SubTag1/SubSubTag1', 'Tag2'], 'title': 'test page'},
        ['title', 'ctime', 'mtime', 'tag']
        ),
        (
        '<head><title>test page</title><meta title="test page"/><meta ctime="202102122352"/><meta mtime="202104242208"/><meta tags="Tag1,Tag1/SubTag1,Tag1/SubTag1/SubSubTag1,Tag2"/></head><h1>This is H1</h1',
        {'ctime': '202102122352', 'mtime': '202104242208',
         'tags': ['Tag1', 'Tag1/SubTag1', 'Tag1/SubTag1/SubSubTag1', 'Tag2'], 'title': 'test page'},
        ['title', 'ctime', 'mtime', 'tags']),
        (
        '<head><title>test page</title><meta title="test page"/><meta ctime="202102122352"/><meta mtime="202104242208"/><meta tags="Tag1,Tag1/SubTag1,Tag1/SubTag1/SubSubTag1,Tag2"/></head><h1>This is H1</h1',
        {'ctime': '202102122352', 'mtime': '202104242208',
         'tags': ['Tag1', 'Tag1/SubTag1', 'Tag1/SubTag1/SubSubTag1', 'Tag2'], 'title': 'test page'},
        [''])
    ]
)
def test_convert_tag_sting_to_tag_list(html_string, expected, schema):
    conversion_settings = ConversionSettings()
    conversion_settings.metadata_schema = schema
    metadata_processor = MetaDataProcessor(conversion_settings)

    metadata_processor.parse_html_metadata(html_string)

    metadata_processor.convert_tag_sting_to_tag_list()

    assert metadata_processor.metadata == expected


@pytest.mark.parametrize(
    'html_string, expected', [
        (
        '<head><title>test page</title><meta title="test page"/><meta ctime="202102122352"/><meta mtime="202104242208"/><meta tag="Tag1,Tag1/SubTag1,Tag1/SubTag1/SubSubTag1,Tag2"/></head><h1>This is H1</h1',
        ['SubSubTag1', 'SubTag1', 'Tag1', 'Tag2']
        ),
        (
        '<head><title>test page</title><meta title="test page"/><meta ctime="202102122352"/><meta mtime="202104242208"/><meta tags="Tag1,Tag1/SubTag1,Tag1/SubTag1/SubSubTag1,Tag2"/></head><h1>This is H1</h1',
        ['SubSubTag1', 'SubTag1', 'Tag1', 'Tag2']
        ),
    ]
)
def test_split_tags_if_required_with_tags_key(html_string, expected):
    conversion_settings = ConversionSettings()
    conversion_settings.split_tags = True
    conversion_settings.metadata_schema = ['']
    metadata_processor = MetaDataProcessor(conversion_settings)

    metadata_processor.parse_html_metadata(html_string)

    metadata_processor.convert_tag_sting_to_tag_list()

    if 'tags' in metadata_processor.metadata:
        assert sorted(metadata_processor.metadata['tags']) == expected

    if 'tag' in metadata_processor.metadata:
        assert sorted(metadata_processor.metadata['tag']) == expected


@pytest.mark.parametrize(
    'content, metadata, front_matter_format, expected', [
        ('Hello',
         {},
         'yaml',
         'Hello',
         ),
        ('Hello',
         {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
         'yaml',
         '---\nexcerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n---\n\nHello',
         ),
        ('Hello',
         {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
         'toml',
         '+++\nexcerpt = "tl;dr"\nlayout = "post"\ntitle = "Hello, world!"\n\n+++\n\nHello',
         ),
        ('Hello',
         {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
         'json',
         '{\n    "excerpt": "tl;dr",\n    "layout": "post",\n    "title": "Hello, world!"\n}\n\n\nHello',
         ),
        ('Hello',
         {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
         'text',
         'excerpt: tl;dr\nlayout: post\ntitle: Hello, world!\n\nHello',
         ),
        ('Hello',
         {'excerpt': 'tl;dr', 'layout': 'post', 'title': 'Hello, world!'},
         'none',
         'Hello',
         ),
    ]
)
def test_add_metadata_md_to_content(content, metadata, front_matter_format, expected):
    conversion_settings = ConversionSettings()
    conversion_settings.front_matter_format = front_matter_format
    metadata_processor = MetaDataProcessor(conversion_settings)
    metadata_processor._metadata = metadata
    result = metadata_processor.add_metadata_md_to_content(content)

    assert result == expected


def test_add_metadata_html_to_content():
    conversion_settings = ConversionSettings()
    conversion_settings.front_matter_format = 'yaml'
    metadata_processor = MetaDataProcessor(conversion_settings)
    metadata_processor._metadata = {'title': 'My Title',
                                    'ctime': '1234',
                                    'mtime': '5678',
                                    'tags':
                                        ["Tag1",
                                         "Tag1/SubTag1",
                                         "Tag1/SubTag1/SubSubTag1",
                                         "Tag2"]
                                    }
    content = """<!DOCTYPE html>

    <html lang="" xml:lang="" xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <meta charset="utf-8"/>
    <meta content="pandoc" name="generator"/>
    <meta content="width=device-width, initial-scale=1.0, user-scalable=yes" name="viewport"/>
    <title>-</title>
    <style>
        html {
          line-height: 1.5;
          font-family: Georgia, serif;
          font-size: 20px;
          color: #1a1a1a;
          background-color: #fdfdfd;
        }
    </style>
    </head></html>
    """

    expected = """<!DOCTYPE html>

<html lang="" xml:lang="" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8"/>
<meta content="pandoc" name="generator"/>
<meta content="width=device-width, initial-scale=1.0, user-scalable=yes" name="viewport"/>
<title>My Title</title>
<style>
        html {
          line-height: 1.5;
          font-family: Georgia, serif;
          font-size: 20px;
          color: #1a1a1a;
          background-color: #fdfdfd;
        }
    </style>
<meta title="My Title"/><meta ctime="1234"/><meta mtime="5678"/><meta tags="Tag1,Tag1/SubTag1,Tag1/SubTag1/SubSubTag1,Tag2"/></head></html>
"""

    result = metadata_processor.add_metadata_html_to_content(content)

    assert result == expected

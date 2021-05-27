import pytest

import config
import conversion_settings
import pandoc_converter


def test_find_pandoc_version(caplog):
    config.set_logger_level('DEBUG')
    cs = conversion_settings.ConversionSettings()
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    caplog.clear()
    pandoc_processor.find_pandoc_version()

    assert len(caplog.records) == 1

    for record in caplog.records:
        assert record.levelname == "DEBUG"


def test_find_pandoc_version_invalid_path_check_sys_exit(caplog):
    config.set_logger_level('DEBUG')
    cs = conversion_settings.ConversionSettings()
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    pandoc_processor._pandoc_path = 'invalid-path'
    caplog.clear()
    with pytest.raises(SystemExit) as exc:
        pandoc_processor.find_pandoc_version()

    assert str(exc.value) == '1'

    assert len(caplog.records) == 1

    for record in caplog.records:
        assert record.levelname == "WARNING"


@pytest.mark.parametrize(
    'version, conversion_input, input_file_format, output_file_format, expected', [
        ('1.15', 'nsx', 'html', 'gfm', 'gfm'),
        ('1.15', 'nsx', 'html', 'obsidian', 'gfm'),
        ('1.15', 'nsx', 'html', 'pandoc_markdown', 'markdown'),
        ('1.15', 'nsx', 'html', 'commonmark', 'commonmark'),
        ('1.15', 'nsx', 'html', 'pandoc_markdown_strict', 'markdown_strict'),
        ('1.15', 'nsx', 'html', 'multimarkdown', 'markdown_mmd'),
        ('1.15', 'nsx', 'html', 'html', 'html'),
    ]
)
def test_generate_pandoc_options_check_pandoc_conversion_option_lookup(caplog, version, conversion_input, input_file_format, output_file_format, expected):
    config.set_logger_level('DEBUG')
    cs = conversion_settings.ConversionSettings()
    cs.conversion_input = conversion_input
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    pandoc_processor._pandoc_version = version
    pandoc_processor.output_file_format = output_file_format
    caplog.clear()
    pandoc_processor.generate_pandoc_options()

    assert len(caplog.records) == 1

    for record in caplog.records:
        assert record.levelname == "DEBUG"

    assert pandoc_processor.pandoc_options[-2] == expected


@pytest.mark.parametrize(
    'version, conversion_input, markdown_conversion_input, output_file_format, expected', [
        ('1.15', 'nsx', 'html', 'gfm', 'html'),
        ('1.15', 'html', 'html', 'obsidian', 'html'),
        ('1.15', 'markdown', 'pandoc_markdown', 'gfm', 'markdown'),
    ]
)
def test_generate_pandoc_options_check_conversion_input_format_setting(caplog, version, conversion_input, markdown_conversion_input, output_file_format, expected):
    config.set_logger_level('DEBUG')
    cs = conversion_settings.ConversionSettings()
    cs.conversion_input = conversion_input
    cs.markdown_conversion_input = markdown_conversion_input
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    pandoc_processor._pandoc_version = version
    pandoc_processor.output_file_format = output_file_format
    caplog.clear()
    pandoc_processor.generate_pandoc_options()

    assert len(caplog.records) == 1

    for record in caplog.records:
        assert record.levelname == "DEBUG"

    assert pandoc_processor.pandoc_options[2] == expected


@pytest.mark.parametrize(
    'version, conversion_input, input_file_format, output_file_format, expected', [
        ('1.15', 'nsx', 'html', 'gfm', ['gfm', '--no-wrap']),
        ('1.16', 'nsx', 'html', 'gfm', ['--wrap=none', '-o']),
        ('1.18', 'nsx', 'html', 'gfm', ['--wrap=none', '-o']),
        ('1.19', 'nsx', 'html', 'gfm', ['--wrap=none', '--atx-headers']),
        ('1.20', 'nsx', 'html', 'gfm', ['--wrap=none', '--atx-headers']),
        ('2.11.1', 'nsx', 'html', 'gfm', ['--wrap=none', '--atx-headers']),
        ('2.11.2', 'nsx', 'html', 'gfm', ['--wrap=none', '--markdown-headings=atx']),
        ('2.13', 'nsx', 'html', 'gfm', ['--wrap=none', '--markdown-headings=atx']),
    ]
)
def test_generate_pandoc_options_check_pandoc_version_conversion_settings(caplog, version, conversion_input, input_file_format, output_file_format, expected):
    config.set_logger_level('DEBUG')
    cs = conversion_settings.ConversionSettings()
    cs.conversion_input = conversion_input
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    pandoc_processor._pandoc_version = version
    pandoc_processor.output_file_format = output_file_format
    caplog.clear()
    pandoc_processor.generate_pandoc_options()

    assert len(caplog.records) == 1

    for record in caplog.records:
        assert record.levelname == "DEBUG"

    assert pandoc_processor.pandoc_options[-2:] == expected


def test_is_pandoc_installed_valid_path(caplog):
    cs = conversion_settings.ConversionSettings()
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    pandoc_processor._pandoc_path = 'pandoc'
    caplog.clear()
    result = pandoc_processor.is_pandoc_installed()

    assert result


def test_is_pandoc_installed_invalid_path(caplog):
    cs = conversion_settings.ConversionSettings()
    pandoc_processor = pandoc_converter.PandocConverter(cs)
    pandoc_processor._pandoc_path = 'invalid-path'
    caplog.clear()
    result = pandoc_processor.is_pandoc_installed()

    assert not result

    assert len(caplog.records) == 1

    for record in caplog.records:
        assert record.levelname == "WARNING"


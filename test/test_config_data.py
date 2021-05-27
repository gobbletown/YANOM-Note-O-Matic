from pathlib import Path

import pytest

import config_data
from conversion_settings import ConversionSettings

@pytest.fixture
def good_config_ini() -> str:
    return """[conversion_inputs]
    # valid entries are nsx, html, markdown
    #  nsx = synology note station export file
    #  html = simple html based notes pages, no complex css or javascript
    #  markdown =  text files in markdown format
conversion_input = nsx

[markdown_conversion_inputs]
    # valid entries are obsidian, gfm, commonmark, q_own_notes, pandoc_markdown_strict, pandoc_markdown, multimarkdown
markdown_conversion_input = obsidian

[quick_settings]
    # valid entries are q_own_notes, obsidian, gfm, pandoc_markdown, commonmark, pandoc_markdown_strict, multimarkdown, html
    # use manual to use the manual settings in the sections below
    # note if an option other than - manual - is used the rest of the 
    # settings in this file will be set automatically
    #
quick_setting = obsidian
    # 
    # the following sections only apply if the above is set to manual
    #  

[export_formats]
    # valid entries are q_own_notes, obsidian, gfm, pandoc_markdown, commonmark, pandoc_markdown_strict, multimarkdown, html
export_format = obsidian

[meta_data_options]
    # note: front_matter_format sets the presence and type of the section with metadata 
    #retrieved from the source
    # valid entries are yaml, toml, json, text, none
    # no entry will result in no front matter section
front_matter_format = yaml
    # metadata schema is a comma separated list of metadata keys that you wish to 
    # restrict the retrieved metadata keys. for example 
    # title, tags    will return those two if they are found
    # if left blank any meta data found will be used
    # the useful available keys in an nsx file are title, ctime, mtime, tag
metadata_schema = title,ctime,mtime,tag
    # tag prefix is a character you wish to be added to the front of any tag values 
    # retrieved from metadata.  note this is only used if front_matter_format is none
tag_prefix = #
    # spaces_in_tags if true will maintain spaces in tag words, if false spaces are replaced by a dash -
spaces_in_tags = False
    # split tags will split grouped tags into individual tags if true
    # "tag1", "tag1/sub tag2"  will become "tag1", "sub tag2"
    # grouped tags are only split where a "/" character is found
split_tags = False

[table_options]
  #  these two table options apply to nsx files only
first_row_as_header = True
first_column_as_header = True

[chart_options]
  #  these three chart options apply to nsx files only
chart_image = True
chart_csv = True
chart_data_table = True

[file_options]
source = my_source
export_folder_name = notes
attachment_folder_name = attachments
creation_time_in_exported_file_name = False
    # creation time in file name only applies to nsx files.
    # if true creation time as `yyyymmddhhmm-` will be added as prefix to file name

"""


def test_initialisation(tmp_path):
    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    assert isinstance(cd, config_data.ConfigData)


def test_read_config_file_file_missing(tmp_path, caplog):
    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    caplog.clear()

    cd.read_config_file()

    assert cd.conversion_settings.export_format == 'gfm'

    assert len(caplog.records) > 0

    for record in caplog.records:
        if record.levelname == "WARNING":
            assert 'config.ini missing, generating new file' in record.message


def test_read_config_file_good_file(tmp_path, good_config_ini, caplog):

    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.read_config_file()

    assert len(caplog.records) > 0

    for record in caplog.records:
        assert record.levelname == "INFO"

    assert cd['conversion_inputs']['conversion_input'] == 'nsx'
    assert cd['markdown_conversion_inputs']['markdown_conversion_input'] == 'obsidian'
    assert cd['quick_settings']['quick_setting'] == 'obsidian'
    assert cd['export_formats']['export_format'] == 'obsidian'
    assert cd['meta_data_options']['front_matter_format'] == 'yaml'
    assert cd['meta_data_options']['metadata_schema'] == 'title,ctime,mtime,tag'
    assert cd['meta_data_options']['tag_prefix'] == '#'
    assert cd.getboolean('meta_data_options', 'spaces_in_tags') is False
    assert cd.getboolean('meta_data_options', 'split_tags') is False
    assert cd.getboolean('table_options', 'first_row_as_header') is True
    assert cd.getboolean('table_options', 'first_column_as_header') is True
    assert cd.getboolean('chart_options', 'chart_image') is True
    assert cd.getboolean('chart_options', 'chart_csv') is True
    assert cd.getboolean('chart_options', 'chart_data_table') is True
    assert cd['file_options']['source'] == 'my_source'
    assert cd['file_options']['export_folder_name'] == 'notes'
    assert cd['file_options']['attachment_folder_name'] == 'attachments'
    assert cd.getboolean('file_options', 'creation_time_in_exported_file_name') is False


def test_validate_config_file_good_file(tmp_path, good_config_ini):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.read_config_file()
    valid_config = cd.validate_config_file()
    assert valid_config


@pytest.mark.parametrize(
    'key1, key2, bad_value', [
        ('conversion_inputs', 'conversion_input', 'bad-value-1234'),
        ('markdown_conversion_inputs', 'markdown_conversion_input', 'bad-value-1234'),
        ('quick_settings', 'quick_setting', 'bad-value-1234'),
        ('export_formats', 'export_format', 'bad-value-1234'),
        ('meta_data_options', 'front_matter_format', 'bad-value-1234'),
        ('meta_data_options', 'spaces_in_tags', 'bad-value-1234'),
        ('meta_data_options', 'split_tags', 'bad-value-1234'),
        ('table_options', 'first_row_as_header', 'bad-value-1234'),
        ('table_options', 'first_column_as_header', 'bad-value-1234'),
        ('chart_options', 'chart_image', 'bad-value-1234'),
        ('chart_options', 'chart_csv', 'bad-value-1234'),
        ('chart_options', 'chart_data_table', 'bad-value-1234'),
        ('file_options', 'creation_time_in_exported_file_name', 'bad-value-1234'),
    ]
)
def test_validate_config_file_bad_values(tmp_path, good_config_ini, key1, key2, bad_value):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.read_config_file()
    cd[key1][key2] = bad_value
    valid_config = cd.validate_config_file()
    assert valid_config is False




@pytest.mark.parametrize(
    'key1, key2, start_value, end_value, expected', [
        ('conversion_inputs', 'conversion_input', 'nsx', 'html', 'html'),
        ('markdown_conversion_inputs', 'markdown_conversion_input', 'obsidian', 'gfm', 'gfm'),
        ('quick_settings', 'quick_setting', 'obsidian', 'commonmark', 'commonmark'),
        ('export_formats', 'export_format', 'obsidian', 'multimarkdown', 'multimarkdown'),
        ('meta_data_options', 'front_matter_format', 'yaml', 'toml', 'toml'),
        ('meta_data_options', 'metadata_schema', 'title,ctime,mtime,tag', 'something_different', ['something_different']),
        ('meta_data_options', 'tag_prefix', '#', '@', '@'),
        ('meta_data_options', 'spaces_in_tags', 'False', 'True', True),
        ('meta_data_options', 'split_tags', 'False', 'True', True),
        ('table_options', 'first_row_as_header', 'True', 'False', False),
        ('table_options', 'first_column_as_header', 'True', 'False', False),
        ('chart_options', 'chart_image', 'True', 'False', False),
        ('chart_options', 'chart_csv', 'True', 'False', False),
        ('chart_options', 'chart_data_table', 'True', 'False', False),
        # ('file_options', 'source', 'my_source', 'new_source', 'new_source'),
        ('file_options', 'export_folder_name', 'export_orig', 'export_new', Path('export_new')),
        ('file_options', 'attachment_folder_name', 'attachment_orig', 'attachment_new', Path('attachment_new')),
        ('file_options', 'creation_time_in_exported_file_name', 'True', 'False', False),
    ]
)
def test_generate_conversion_settings_from_parsed_config_file_data(good_config_ini, tmp_path, key1, key2, start_value, end_value, expected):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.read_config_file()

    # empty the source entry for config data as will cause error when generating conversion settings
    cd['file_options']['source'] = ''

    # set start value for conversion setting
    setattr(cd.conversion_settings, key2, start_value)
    # change value as if read from another file
    cd[key1][key2] = end_value
    # convert config parser object to conversion settings
    cd.generate_conversion_settings_from_parsed_config_file_data()
    # confirm conversion setting has changed
    assert getattr(cd.conversion_settings, key2) == expected


def test_generate_conversion_settings_from_parsed_config_file_data_test_source_setting(good_config_ini, tmp_path):
    # by inducing a system exit we know the new path was passed into config_settings correctly
    # the error is raised when the source setter sees an invalid path
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.read_config_file()

    # set the source location
    cd['file_options']['source'] = 'new_source'

    # confirm conversion_settings source is empty
    assert cd.conversion_settings.source == ''

    # convert config parser object to conversion settings
    with pytest.raises(SystemExit) as exc:
        cd.generate_conversion_settings_from_parsed_config_file_data()

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'


def test_conversion_settings_proprty_obj_confirm_obj_read(tmp_path, good_config_ini):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cs = ConversionSettings()

    cs.quick_set_multimarkdown_settings()

    cd.conversion_settings = cs

    assert cd.conversion_settings.export_format == 'multimarkdown'
    assert cd['export_formats']['export_format'] == 'multimarkdown'


def test_conversion_settings_proprty_obj_confirm_config_file_written(tmp_path, good_config_ini):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cs = ConversionSettings()

    cs.quick_set_multimarkdown_settings()

    cd.conversion_settings = cs

    cd.read_config_file()

    assert cd['export_formats']['export_format'] == 'multimarkdown'


def test_conversion_settings_proprty_obj_confirm_string_setting(tmp_path, good_config_ini):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.conversion_settings = 'multimarkdown'

    assert cd.conversion_settings.export_format == 'multimarkdown'
    assert cd['export_formats']['export_format'] == 'multimarkdown'


def test_conversion_settings_proprty_string_setting_confirm_config_file_written(tmp_path, good_config_ini):
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cs = ConversionSettings()

    cd.conversion_settings = 'multimarkdown'

    cd.read_config_file()

    assert cd['export_formats']['export_format'] == 'multimarkdown'


def test_parse_config_file(good_config_ini, tmp_path):

    good_config_ini = good_config_ini.replace('source = my_source', 'source = ')

    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.parse_config_file()

    assert cd.conversion_settings.export_format == 'obsidian'


def test_ask_user_to_choose_new_default_config_file_user_choose_exit(good_config_ini, tmp_path, monkeypatch):
    import interactive_cli

    def patched_cli(ignored):
        return 'exit'

    good_config_ini = good_config_ini.replace('source = my_source', 'source = ')

    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    monkeypatch.setattr(interactive_cli.InvalidConfigFileCommandLineInterface, 'run_cli', patched_cli)

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    with pytest.raises(SystemExit) as exc:
        cd.ask_user_to_choose_new_default_config_file()

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '0'


def test_ask_user_to_choose_new_default_config_file_user_choose_exit(good_config_ini, tmp_path, monkeypatch):
    import interactive_cli

    def patched_cli(ignored):
        return 'default'

    good_config_ini = good_config_ini.replace('source = my_source', 'source = ')

    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")

    monkeypatch.setattr(interactive_cli.InvalidConfigFileCommandLineInterface, 'run_cli', patched_cli)

    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)

    cd.ask_user_to_choose_new_default_config_file()

    assert cd.conversion_settings.export_format == 'gfm'


def test_str(good_config_ini, tmp_path):
    good_config_ini = good_config_ini.replace('source = my_source', 'source = ')
    Path(f'{str(tmp_path)}/config.ini').write_text(good_config_ini, encoding="utf-8")
    cd = config_data.ConfigData(f"{str(tmp_path)}/config.ini", 'gfm', allow_no_value=True)
    cd.parse_config_file()

    result = str(cd)
    assert result == "ConfigData{'conversion_inputs': {'conversion_input': 'nsx'}, 'markdown_conversion_inputs': {'markdown_conversion_input': 'obsidian'}, 'quick_settings': {'quick_setting': 'obsidian'}, 'export_formats': {'export_format': 'obsidian'}, 'meta_data_options': {'front_matter_format': 'yaml', 'metadata_schema': 'title,ctime,mtime,tag', 'tag_prefix': '#', 'spaces_in_tags': 'False', 'split_tags': 'False'}, 'table_options': {'first_row_as_header': 'True', 'first_column_as_header': 'True'}, 'chart_options': {'chart_image': 'True', 'chart_csv': 'True', 'chart_data_table': 'True'}, 'file_options': {'source': '', 'export_folder_name': 'notes', 'attachment_folder_name': 'attachments', 'creation_time_in_exported_file_name': 'False'}}"
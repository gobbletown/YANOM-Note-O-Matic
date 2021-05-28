import json
from pathlib import Path
import zipfile

import config
import pytest

import zip_file_reader


def test_read_json_data(tmp_path):
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = {'key': 'value'}
    target_filename = 'file.txt'

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.writestr(target_filename, json.dumps(expected))

    result = zip_file_reader.read_json_data(zip_filename, target_filename)

    assert result == expected


def test_read_binary_file(tmp_path):
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = b'Hello World'
    target_filename = 'file.bin'

    with open(Path(tmp_path, target_filename), "wb") as file:
        file.write(expected)

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.write(Path(tmp_path, target_filename), target_filename)

    result = zip_file_reader.read_binary_file(zip_filename, target_filename)

    assert result == expected


def test_read_binary_file_bad_file_name(tmp_path, caplog, capfd):
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = b'Hello World'
    target_filename = 'file.bin'

    with open(Path(tmp_path, target_filename), "wb") as file:
        file.write(expected)

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.write(Path(tmp_path, target_filename), target_filename)

    with pytest.raises(SystemExit) as exc:
        result = zip_file_reader.read_binary_file(zip_filename, 'bad_file_name')

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'

    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "ERROR"

    assert ('Error - unable to find the file ' in caplog.records[1].message)

    out, err = capfd.readouterr()
    assert 'Error - unable to find the file ' in out
    assert err == ''


def test_read_binary_file_bad_zip_file_name(tmp_path, caplog, capfd):
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = b'Hello World'
    target_filename = 'file.bin'

    with open(Path(tmp_path, target_filename), "wb") as file:
        file.write(expected)

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.write(Path(tmp_path, target_filename), target_filename)

    with pytest.raises(SystemExit) as exc:
        result = zip_file_reader.read_binary_file('bad_file_name', target_filename)

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'

    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "ERROR"

    assert ('Error - unable to read zip file ' in caplog.records[1].message)

    out, err = capfd.readouterr()
    assert 'Error - unable to read zip file ' in out
    assert err == ''


def test_read_json_data_bad_zip_file_name(tmp_path, caplog, capfd):
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = {'key': 'value'}
    target_filename = 'file.txt'

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.writestr(target_filename, json.dumps(expected))

    with pytest.raises(SystemExit) as exc:
        result = zip_file_reader.read_json_data('bad_file_name', target_filename)

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'

    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "ERROR"

    assert ('Error - unable to read zip file ' in caplog.records[1].message)

    out, err = capfd.readouterr()
    assert 'Error - unable to read zip file ' in out
    assert err == ''


def test_read_json_data_bad_file_name(tmp_path, caplog, capfd):
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = {'key': 'value'}
    target_filename = 'file.txt'

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.writestr(target_filename, json.dumps(expected))

    with pytest.raises(SystemExit) as exc:
        result = zip_file_reader.read_json_data(zip_filename, 'bad_file_name')

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'

    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "ERROR"

    assert ('Error - unable to find the file ' in caplog.records[1].message)

    out, err = capfd.readouterr()
    assert 'Error - unable to find the file ' in out
    assert err == ''


def test_read_json_data_bad_zip_file_name_in_silent_mode(tmp_path, caplog, capfd):
    config.set_silent(True)
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = {'key': 'value'}
    target_filename = 'file.txt'

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.writestr(target_filename, json.dumps(expected))

    with pytest.raises(SystemExit) as exc:
        result = zip_file_reader.read_json_data('bad_file_name', target_filename)

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'

    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "ERROR"

    assert ('Error - unable to read zip file ' in caplog.records[1].message)

    out, err = capfd.readouterr()
    assert '' in out
    assert err == ''


def test_read_json_data_bad_file_name_in_silent_mode(tmp_path, caplog, capfd):
    config.set_silent(True)
    zip_filename = Path(tmp_path, 'test_zip.zip')
    expected = {'key': 'value'}
    target_filename = 'file.txt'

    with zipfile.ZipFile(str(zip_filename), 'w') as zip_file:
        zip_file.writestr(target_filename, json.dumps(expected))

    with pytest.raises(SystemExit) as exc:
        result = zip_file_reader.read_json_data(zip_filename, 'bad_file_name')

    assert isinstance(exc.type, type(SystemExit))
    assert str(exc.value) == '1'

    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "ERROR"

    assert ('Error - unable to find the file ' in caplog.records[1].message)

    out, err = capfd.readouterr()
    assert '' in out
    assert err == ''
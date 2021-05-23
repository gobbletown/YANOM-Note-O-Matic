from pathlib import Path
import file_writer
from io import BytesIO


def test_file_writer_string(tmp_path):
    content = "Hello World"
    file_path = Path(tmp_path, "file1.file")
    file_writer.store_file(file_path, content)

    result = file_path.read_text()

    assert result == content


def test_file_writer_string_invalid_path(tmp_path, caplog):
    content = "Hello World"
    file_path = Path(tmp_path,"ddsf/dsfsdf/dfsd", "file1.file")
    file_writer.store_file(file_path, content)

    assert len(caplog.records) > 0

    for record in caplog.records:
        assert record.levelname == "ERROR"


def test_file_writer_bytes(tmp_path):
    content = b'Hello World'
    file_path = Path(tmp_path, "file1.file")
    file_writer.store_file(file_path, content)

    result = file_path.read_bytes()

    assert result == content


def test_file_writer_bytes_invalid_path(tmp_path, caplog):
    content = b'Hello World'
    file_path = Path(tmp_path, "ddsf/dsfsdf/dfsd", "file1.file")
    file_writer.store_file(file_path, content)

    assert len(caplog.records) > 0

    for record in caplog.records:
        assert record.levelname == "ERROR"


def test_file_writer_bytes_io(tmp_path):
    content = BytesIO(b"Hello World")
    file_path = Path(tmp_path, "file1.file")
    file_writer.store_file(file_path, content)

    result = file_path.read_bytes()

    assert result == b"Hello World"


def test_file_writer_bytes_io_invalid_path(tmp_path, caplog):
    content = BytesIO(b"Hello World")
    file_path = Path(tmp_path, "ddsf/dsfsdf/dfsd", "file1.file")
    file_writer.store_file(file_path, content)

    assert len(caplog.records) > 0

    for record in caplog.records:
        assert record.levelname == "ERROR"


def test_file_writer_invalid_type_content(tmp_path, caplog):
    content = 23
    file_path = Path(tmp_path, "file1.file")
    file_writer.store_file(file_path, content)

    assert len(caplog.records) > 0

    for record in caplog.records:
        assert record.levelname == "WARNING"

import io
from io import StringIO
import unittest
from unittest.mock import patch
import sys
import contextlib
import pytest

from src.arg_parsing import CommandLineParsing
from src.globals import VERSION


# class ParserTest(unittest.TestCase):
#     # def setUp(self) -> None:
#     #     self.parser = CommandLineParsing()

    def test_parse_args(self):
        self.parser.parse_args(['-s', '-i', '--source', 'hello'])
        self.assertTrue(self.parser.args['silent'], 'Failed to set ini argument')
        self.assertTrue(self.parser.args['ini'], 'Failed to set ini argument')
        self.assertEqual(self.parser.args['source'], 'hello', 'Failed to set source argument')

        self.parser.parse_args(['-c', '--source', 'hello'])
        self.assertTrue(self.parser.args['cli'], 'Failed to set cli argument')
        self.assertEqual(self.parser.args['source'], 'hello', 'Failed to set source argument')

        # self.parser.parse_args(['-v'])
        # self.assertEqual(self.parser.args['version'], 'yanom.py Version 1.0', 'Failed to set source argument')

    def test_should_exit_with_invalid_arg(self):
        parser = CommandLineParsing()
        with pytest.raises(SystemExit) as exc_info:
            # parser.parse_args(['--invalid'])
            parser.parse_args(['-s'])
        # assert "unrecognized arguments" in str(exc_info.value)


    def test_should_exit(self):
        fake_output = io.StringIO()
        with contextlib.redirect_stdout(fake_output):
            try:
                self.parser.parse_args(['--invalid'])
                # self.parser.parse_args(['-s'])
            except BaseException as e:
                self.assertEqual(type(e), SystemExit)
                my_error = fake_output.getvalue()
                pass
            else:
                self.assertTrue(False, 'No exception was raised for invalid argument')



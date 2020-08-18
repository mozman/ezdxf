# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from io import BytesIO
from ezdxf.recover import bytes_loader, detect_encoding

HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1027
  9
$ACADMAINTVER
 70
105
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
TEST
  1
ÄÖÜ
"""


class TestBytesLoader:
    @pytest.fixture
    def data(self):
        return BytesIO(HEADER.encode('latin1'))

    def test_bytes_loader(self, data):
        result = list(bytes_loader(data))
        assert len(result) == 10
        assert result[-1] == (1, b'\xc4\xd6\xdc')

    def test_encoding_detector(self, data):
        assert detect_encoding(bytes_loader(data)) == 'utf8'

    def test_windows_line_endings_CR_LF(self):
        tags = list(bytes_loader(BytesIO(b"0\r\n1\r\n0\r\n2\r\n")))
        assert tags == [(0, b'1'), (0, b'2')], \
            "Windows line endings CR/LF must be supported."

    def test_linux_and_macos_x_line_endings_LF(self):
        tags = list(bytes_loader(BytesIO(b"0\n1\n0\n2\n")))
        assert tags == [(0, b'1'), (0, b'2')], \
            "Linux and MacOS X line endings LF must be supported."

    def test_line_endings_only_CR(self):
        tags = list(bytes_loader(BytesIO(b"0\r1\r0\r2\r")))
        assert tags == [], \
            "MaxOS prior to MacOS X line endings CR are not supported."

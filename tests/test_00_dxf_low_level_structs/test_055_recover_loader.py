# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from io import BytesIO
from ezdxf.recover import bytes_loader, detect_encoding, synced_bytes_loader
from ezdxf.lldxf import const

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
    @pytest.fixture(params=[bytes_loader, synced_bytes_loader])
    def loader(self, request):
        return request.param

    @pytest.fixture
    def data(self):
        return BytesIO(HEADER.encode('latin1'))

    def test_bytes_loader(self, data, loader):
        result = list(loader(data))
        assert len(result) == 10
        assert result[-1] == (1, b'\xc4\xd6\xdc')

    def test_encoding_detector(self, data, loader):
        assert detect_encoding(loader(data)) == 'utf8'

    def test_windows_line_endings_CR_LF(self, loader):
        tags = list(loader(BytesIO(b"0\r\n1\r\n0\r\n2\r\n")))
        assert tags == [(0, b'1'), (0, b'2')], \
            "Windows line endings CR/LF must be supported."

    def test_linux_and_macos_x_line_endings_LF(self, loader):
        tags = list(bytes_loader(BytesIO(b"0\n1\n0\n2\n")))
        assert tags == [(0, b'1'), (0, b'2')], \
            "Linux and MacOS X line endings LF must be supported."

    def test_line_endings_only_CR(self):
        with pytest.raises(const.DXFStructureError):
            list(bytes_loader(BytesIO(b"0\r1\r0\r2\r")))

        assert list(synced_bytes_loader(BytesIO(b"0\r1\r0\r2\r"))) == [], \
            "MacOS prior to MacOS X line endings CR are not supported."


OUT_OF_SYNC_TAGS = """
  0
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
test
"""


def test_out_of_sync_tags():
    result = list(synced_bytes_loader(
        BytesIO(OUT_OF_SYNC_TAGS.encode())))
    assert len(result) == 10

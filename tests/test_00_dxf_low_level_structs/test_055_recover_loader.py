# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import itertools
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


@pytest.fixture
def data():
    return BytesIO(HEADER.encode('latin1'))


def test_bytes_loader(data):
    result = list(bytes_loader(data))
    assert len(result) == 10
    assert result[-1] == (1, b'\xc4\xd6\xdc')


def test_encoding_detector(data):
    assert detect_encoding(bytes_loader(data)) == 'utf8'

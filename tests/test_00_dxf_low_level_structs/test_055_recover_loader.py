# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from io import BytesIO
from ezdxf.recover import BytesLoader, encoding_detector

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


@pytest.fixture
def data2():
    return BytesIO(HEADER.encode('utf8'))


def test_bytes_loader(data):
    result = list(BytesLoader(data))
    assert len(result) == 10
    assert result[-1] == (1, 'ÄÖÜ')


def test_enconding_detector(data2):
    loader = BytesLoader(data2)
    result = list(encoding_detector(loader))
    assert len(result) == 10
    assert loader.encoding == 'utf8'
    assert result[-1] == (1, 'ÄÖÜ')

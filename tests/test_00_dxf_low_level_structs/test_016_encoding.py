# Copyright (C) 2016-2020, Manfred Moitzi
# License: MIT License
import pytest
import codecs
from ezdxf.lldxf.encoding import dxf_backslash_replace
from pathlib import Path

# setup DXF unicode encoder -> '\U+nnnn'
codecs.register_error('dxfreplace', dxf_backslash_replace)


def test_ascii_encoding():
    assert b'123\\U+6539' == u'123改'.encode('ascii', errors='dxfreplace')


@pytest.mark.parametrize(['s', 'e'], [
    ('300\n\udcb7\udc9e\udcff\n', b'300\n\xb7\x9e\xff\n'),
    ('123改', b'123\\U+6539')
])
def test_surrogate_escape_support_in_dxf_replace_encoder(s, e):
    assert e == s.encode('ascii', errors='dxfreplace')


@pytest.mark.parametrize('n', [0, 1, 2])
def test_XRECORD_handling_of_dxf_replace_encoder(n):
    XRECORD = Path(__file__).parent / f'XRECORD_{n}.bin'
    with open(XRECORD, 'rb') as f:
        data = f.read()
    s = data.decode('utf8', errors='surrogateescape')
    result = s.encode('utf8', errors='dxfreplace')
    assert data == result

# Created: 26.03.2016
# Copyright (C) 2016-2019, Manfred Moitzi
# License: MIT License
import pytest

import codecs
from ezdxf.lldxf.encoding import dxf_backslash_replace

codecs.register_error('dxfreplace', dxf_backslash_replace)  # setup DXF unicode encoder -> '\U+nnnn'

from ezdxf.lldxf.encoding import encode
from ezdxf.lldxf.const import DXFEncodingError

DEFAULT_ENC = 'utf-8'


class TestEncoding:
    def test_ascii_encoding(self):
        assert b'123' == encode(u'123', 'ascii')

    def test_ascii_encoding_error(self):
        with pytest.raises(DXFEncodingError):
            encode(u'123Ä', 'ascii')

    def test_ignore_ascii_encoding_error(self):
        assert u'123Ä'.encode(DEFAULT_ENC) == encode(u'123Ä', 'ascii', ignore_error=True)

    def test_cp1252_encoding(self):
        assert u'123ÄÜÖ'.encode('cp1252') == encode(u'123ÄÜÖ', 'cp1252')

    def test_cp1252_encoding_error(self):
        with pytest.raises(DXFEncodingError):
            encode(u'更改', 'cp1252')

    def test_cp1252_ignore_encoding_error(self):
        assert u'更改'.encode(DEFAULT_ENC) == encode(u'更改', 'cp1252', ignore_error=True)


class TestACADEncoding:
    def test_ascii_encoding(self):
        assert b'123\\U+6539' == u'123改'.encode('ascii', errors='dxfreplace')

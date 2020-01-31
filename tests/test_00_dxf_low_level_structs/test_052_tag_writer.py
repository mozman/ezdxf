# Copyright (c) 2010-2019 Manfred Moitzi
# License: MIT License
import pytest
from io import StringIO
from ezdxf.lldxf.tagwriter import TagWriter, TagCollector
from ezdxf.lldxf.types import DXFTag, DXFVertex


def setup_stream():
    stream = StringIO()
    tagwriter = TagWriter(stream)
    return stream, tagwriter


def test_write_tag2():
    s, t = setup_stream()
    t.write_tag2(0, 'SECTION')
    result = s.getvalue()
    assert result == '  0\nSECTION\n'


def test_write_tag():
    s, t = setup_stream()
    t.write_tag(DXFTag(0, 'SECTION'))
    result = s.getvalue()
    assert result == '  0\nSECTION\n'


def test_write_point_tag():
    s, t = setup_stream()
    t.write_tag(DXFVertex(10, (7., 8., 9.)))
    result = s.getvalue()
    assert result == ' 10\n7.0\n 20\n8.0\n 30\n9.0\n'


def test_write_str():
    s, t = setup_stream()
    t.write_str(' 10\n7.0\n 20\n8.0\n 30\n9.0\n')
    result = s.getvalue()
    assert result == ' 10\n7.0\n 20\n8.0\n 30\n9.0\n'


def test_write_anything():
    s, t = setup_stream()
    t.write_str('... writes just any nonsense ...')
    result = s.getvalue()
    assert result == '... writes just any nonsense ...'


class TestTagCollector:

    @pytest.fixture
    def t(self):
        return TagCollector()

    def test_write_tag2(self, t):
        t.write_tag2(0, 'SECTION')
        assert t.tags[0] == (0, 'SECTION')

    def test_write_tag(self, t):
        t.write_tag(DXFTag(0, 'SECTION'))
        assert t.tags[0] == (0, 'SECTION')

    def test_write_point_tag(self, t):
        t.write_tag(DXFVertex(10, (7., 8., 9.)))
        assert t.tags[0] == (10, 7.)
        assert t.tags[1] == (20, 8.)
        assert t.tags[2] == (30, 9.)

    def test_write_str(self, t):
        t.write_str(' 10\n7.0\n 20\n8.0\n 30\n9.0\n')
        assert t.tags[0] == (10, 7.)
        assert t.tags[1] == (20, 8.)
        assert t.tags[2] == (30, 9.)

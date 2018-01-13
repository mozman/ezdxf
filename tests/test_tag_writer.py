import pytest

from io import StringIO
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.lldxf.tags import DXFTag


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
    t.write_tag(DXFTag(10, (7., 8., 9.)))
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


if __name__ == '__main__':
    pytest.main([__file__])


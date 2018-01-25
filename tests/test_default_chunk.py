from ezdxf.sections.unsupported import UnsupportedSection
from ezdxf.tools.test import load_section


def setup_stream():
    from io import StringIO
    from ezdxf.lldxf.tagwriter import TagWriter
    stream = StringIO()
    tagwriter = TagWriter(stream)
    return stream, tagwriter


def test_unsupported_section():
    chunk = UnsupportedSection(load_section(TEST_SECTION, 'HEADER'), None)
    s, t = setup_stream()
    chunk.write(t)
    result = s.getvalue()
    assert result == TEST_SECTION


TEST_SECTION = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$INSBASE
 10
0.0
 20
0.0
 30
0.0
  9
$EXTMIN
 10
-100.0
 20
-200.0
 30
-300.0
  9
$EXTMAX
 10
100.0
 20
200.0
 30
300.0
  0
ENDSEC
"""


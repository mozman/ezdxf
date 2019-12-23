# Copyright (c) 2019, Manfred Moitzi
# License: MIT License

from io import StringIO
from ezdxf import comments

DXF = """999
preceding comment
0
SECTION
5
ABBA
999
comment before LINE
0
LINE
5
FEFE
999
comment after LINE
0
EOF
"""


def test_load_only_comments():
    stream = StringIO(DXF)
    tags = list(comments.from_stream(stream))
    assert len(tags) == 3
    assert tags[0] == (999, 'preceding comment')
    assert tags[1] == (999, 'comment before LINE')
    assert tags[2] == (999, 'comment after LINE')


def test_load_handles_and_comments():
    stream = StringIO(DXF)
    tags = list(comments.from_stream(stream, handles=True))
    assert len(tags) == 5
    assert tags[0] == (999, 'preceding comment')
    assert tags[1] == (5, 'ABBA')
    assert tags[2] == (999, 'comment before LINE')
    assert tags[3] == (5, 'FEFE')
    assert tags[4] == (999, 'comment after LINE')


def test_load_structure_and_comments():
    stream = StringIO(DXF)
    tags = list(comments.from_stream(stream, structure=True))
    assert len(tags) == 6
    assert tags[0] == (999, 'preceding comment')
    assert tags[1] == (0, 'SECTION')
    assert tags[2] == (999, 'comment before LINE')
    assert tags[3] == (0, 'LINE')
    assert tags[4] == (999, 'comment after LINE')
    assert tags[5] == (0, 'EOF')

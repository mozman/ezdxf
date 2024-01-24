# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.acad_xrec_roundtrip import RoundtripXRecord, find_section
from ezdxf.entities import XRecord
from ezdxf.lldxf.tags import Tags


@pytest.fixture
def xrecord():
    xrec = XRecord()
    xrec.tags = Tags.from_text(SECTIONS)
    return xrec


def test_init():
    xrec = RoundtripXRecord()
    assert xrec.xrecord is not None


def test_has_section(xrecord):
    rtr = RoundtripXRecord(xrecord)
    assert rtr.has_section("ACAD_XXX") is True
    assert rtr.has_section("ACAD_AAA") is False


def test_add_new_section():
    rtr = RoundtripXRecord()
    rtr.set_section("ACAD_XXX", Tags.from_tuples([(1, "TEXT")]))
    assert rtr.xrecord.tags == [(102, "ACAD_XXX"), (1, "TEXT")]


def test_replace_existing_section(xrecord):
    rtr = RoundtripXRecord(xrecord)
    rtr.set_section("ACAD_XXX", Tags.from_tuples([(70, 7)]))
    assert xrecord.tags == [(102, "ACAD_XXX"), (70, 7), (102, "ACAD_YYY"), (40, 2.0)]


def test_get_section(xrecord):
    rtr = RoundtripXRecord(xrecord)
    assert rtr.get_section("ACAD_XXX") == [(40, 1.0), (1, "TEXT")]
    assert rtr.get_section("ACAD_YYY") == [(40, 2.0)]


def test_discard_existing_section(xrecord):
    rtr = RoundtripXRecord(xrecord)
    rtr.discard("ACAD_XXX")
    assert xrecord.tags == [(102, "ACAD_YYY"), (40, 2.0)]


def test_discard_non_existing_section(xrecord):
    rtr = RoundtripXRecord(xrecord)
    rtr.discard("ACAD_AAA")
    assert xrecord.tags == [
        (102, "ACAD_XXX"),
        (40, 1.0),
        (1, "TEXT"),
        (102, "ACAD_YYY"),
        (40, 2.0),
    ]


def test_locate_section():
    tags = Tags.from_text(SECTIONS)
    start, end = find_section(tags, "ACAD")
    assert start == -1 and end == -1
    start, end = find_section(tags, "ACAD_XXX")
    assert start == 0 and end == 3
    start, end = find_section(tags, "ACAD_YYY")
    assert start == 3 and end == 5


SECTIONS = """102
ACAD_XXX
40
1.0
1
TEXT
102
ACAD_YYY
40
2.0
"""

if __name__ == "__main__":
    pytest.main([__file__])

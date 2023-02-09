# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest

from ezdxf.entities.appdata import Reactors
from ezdxf.lldxf.const import (
    REACTOR_HANDLE_CODE,
    ACAD_REACTORS,
    APP_DATA_MARKER,
)
from ezdxf.lldxf.tags import Tags


class TagWriter:
    """Mockup"""

    def __init__(self):
        self.tags = []

    def write_tag2(self, code, value):
        self.tags.append((code, value))


def test_reactors_new():
    reactors = Reactors(["DDDD", "AA", "CCCC", "BBB"])
    assert len(reactors) == 4
    handles = reactors.get()
    # sorted handles
    assert handles[0] == "AA"
    assert handles[3] == "DDDD"


def test_reactors_add():
    reactors = Reactors(["AA", "BBB", "CCCC"])
    reactors.add("AA")
    assert len(reactors) == 3, "do not add duplicates"
    reactors.add("0")
    assert len(reactors) == 4, "add unique handles"


def test_reactors_set():
    reactors = Reactors()
    assert len(reactors) == 0
    reactors.set(["0", "1", "2"])
    assert len(reactors) == 3
    reactors.set(["0"])
    assert len(reactors) == 1
    # delete all
    reactors.set([])
    assert len(reactors) == 0


def test_reactors_discard():
    reactors = Reactors(["AA", "BBB", "CCCC"])
    reactors.discard("AA")
    assert len(reactors) == 2

    # ignore non existing handles
    reactors.discard("abcd")
    assert len(reactors) == 2


def test_export_dxf():
    reactors = Reactors(["AA", "BBB", "CCCC"])
    tagwriter = TagWriter()
    reactors.export_dxf(tagwriter)
    tags = tagwriter.tags
    assert len(tags) == 5
    # sorted handles!
    assert tags[0] == (APP_DATA_MARKER, ACAD_REACTORS)
    assert tags[1] == (REACTOR_HANDLE_CODE, "AA")
    assert tags[2] == (REACTOR_HANDLE_CODE, "BBB")
    assert tags[3] == (REACTOR_HANDLE_CODE, "CCCC")
    assert tags[4] == (APP_DATA_MARKER, "}")


def test_from_tags():
    reactors = Reactors.from_tags(Tags.from_text(HANDLES))
    handles = reactors.get()
    assert len(handles) == 3
    assert handles[0] == "C000"
    assert handles[1] == "D000"
    assert handles[2] == "E000"


HANDLES = """102
{ACAD_REACTORS
330
D000
330
C000
330
E000
102
}
"""


if __name__ == "__main__":
    pytest.main([__file__])

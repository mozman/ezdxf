# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities.copy import (
    CopyStrategy,
    CopySettings,
    default_copy,
    CopyNotSupported,
)
from ezdxf.entities import Line, DXFObject
from ezdxf.layouts import Modelspace


class UnknownEntity(DXFObject):
    def copy(self, copy_strategy=default_copy):
        raise CopyNotSupported()


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


@pytest.fixture(scope="module")
def msp(doc) -> Modelspace:
    return doc.modelspace()


def test_basic_copy(msp):
    line = msp.add_line(
        (0, 0),
        (10, 0),
        dxfattribs={
            "layer": "MyLayer",
        },
    )
    strategy = CopyStrategy(CopySettings())
    line2 = strategy.copy(line)

    assert line2 is not None
    assert line2 is not line

    assert line2.dxf.start == (0, 0)
    assert line2.dxf.end == (10, 0)
    assert line2.dxf.layer == "MyLayer"


def test_ignore_errors_in_linked_entities(msp: Modelspace):
    line = msp.add_line((0, 0), (10, 0))
    xdict = line.new_extension_dict()
    dictionary = xdict.dictionary
    dictionary["MyKey"] = UnknownEntity()
    clone = line.copy(default_copy)

    xdict = clone.get_extension_dict()
    keys = list(xdict.keys())
    assert len(keys) == 0, "unsupported entry was not copyied"


def test_raise_copy_not_supported_exception(msp: Modelspace):
    line = msp.add_line((0, 0), (10, 0))
    xdict = line.new_extension_dict()
    dictionary = xdict.dictionary
    dictionary["MyKey"] = UnknownEntity()
    copy_strategy = CopyStrategy(
        CopySettings(ignore_copy_errors_in_linked_entities=False)
    )
    with pytest.raises(CopyNotSupported):
        line.copy(copy_strategy)


if __name__ == "__main__":
    pytest.main([__file__])

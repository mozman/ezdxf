#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import random

import ezdxf
from ezdxf.document import Drawing
from ezdxf import xref, units
from ezdxf.math import Vec3


FLAG_NAME = "Flag"


def test_xref_doc_has_required_properties(host_doc, xref_doc):
    assert xref_doc.dxfversion == host_doc.dxfversion, "same DXF version expected"
    flag = host_doc.blocks.get(FLAG_NAME)
    assert flag is not None
    assert xref_doc.units == flag.units, "same units as source block expected"
    assert xref_doc.units == units.MM, "mm as unity expected"
    assert Vec3(xref_doc.header["$INSBASE"]).isclose(
        (2, 1)
    ), "XREF has invalid base point"


def test_detached_dxf_contains_all_block_entities(xref_doc: Drawing):
    msp = xref_doc.modelspace()
    types = [e.dxftype() for e in msp]
    assert types == ["POLYLINE", "CIRCLE", "ATTDEF", "ATTDEF", "ATTDEF"]


def test_xref_doc_has_required_resources(xref_doc: Drawing):
    assert xref_doc.layers.has_entry("FLAG_SYMBOL")
    assert xref_doc.layers.has_entry("FLAG_ATTRIBS")


def test_source_block_is_empty(host_doc: Drawing):
    flag = host_doc.blocks.get(FLAG_NAME)
    assert flag is not None, "source block should exist"
    assert len(flag) == 0, "source block should be empty"


def get_random_point():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


FLAG_SYMBOL = [(0, 0), (0, 5), (4, 3), (0, 3)]
SAMPLE_COORDS = [get_random_point() for x in range(50)]


@pytest.fixture(scope="module")
def host_doc() -> Drawing:
    doc = ezdxf.new("R2007", units=units.M)
    doc.layers.add("FLAGS")
    doc.layers.add("FLAG_SYMBOL")
    doc.layers.add("FLAG_ATTRIBS")
    msp = doc.modelspace()

    flag = doc.blocks.new(name=FLAG_NAME)
    flag.units = units.MM
    flag.base_point = (2, 1)

    # Add dxf entities to the block (the flag).
    flag.add_polyline2d(FLAG_SYMBOL, dxfattribs={"layer": "FLAG_SYMBOL"})
    flag.add_circle(
        center=(0, 0), radius=0.4, dxfattribs={"layer": "FLAG_SYMBOL", "color": 1}
    )

    # Create the ATTRIB templates as ATTDEF entities:
    flag.add_attdef(
        tag="NAME",
        insert=(0.5, -0.5),
        height=0.5,
        dxfattribs={"layer": "FLAG_ATTRIBS", "color": 3},
    )
    flag.add_attdef(
        tag="XPOS",
        insert=(0.5, -1.0),
        height=0.25,
        dxfattribs={"layer": "FLAG_ATTRIBS", "color": 4},
    )
    flag.add_attdef(
        tag="YPOS",
        insert=(0.5, -1.5),
        height=0.25,
        dxfattribs={"layer": "FLAG_ATTRIBS", "color": 4},
    )

    for number, point in enumerate(SAMPLE_COORDS):
        # Create the value dictionary for the ATTRIB entities, key is the tag
        # name of the ATTDEF entity and the value is the content string of the
        # ATTRIB entity:
        values = {
            "NAME": f"P({number + 1})",
            "XPOS": f"x = {point[0]:.3f}",
            "YPOS": f"y = {point[1]:.3f}",
        }
        random_scale = 0.5 + random.random() * 2.0
        block_ref = msp.add_blockref(
            "FLAG", point, dxfattribs={"layer": "FLAGS", "rotation": -15}
        ).set_scale(random_scale)
        block_ref.add_auto_attribs(values)
    doc.set_modelspace_vport(height=200)
    return doc


@pytest.fixture(scope="module")
def xref_doc(host_doc: Drawing) -> Drawing:
    flag = host_doc.blocks.get(FLAG_NAME)
    assert flag is not None
    return xref.detach(flag, xref_filename="flag_block.dxf")


if __name__ == "__main__":
    pytest.main([__file__])

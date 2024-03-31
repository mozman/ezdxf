# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
import ezdxf.xref
from ezdxf.document import Drawing
from ezdxf.entities import Solid3d
from ezdxf.render import forms


def source_doc_R2007() -> Drawing:
    doc = ezdxf.new("R2007")
    msp = doc.modelspace()
    forms.cube().render_3dsolid(msp)
    return doc


def source_doc_R2013() -> Drawing:
    doc = ezdxf.new("R2013")
    msp = doc.modelspace()
    forms.cube().render_3dsolid(msp)
    return doc


def test_load_acis_from_R2007():
    target_doc = ezdxf.new("R2007")
    source_doc = source_doc_R2007()
    source_msp = source_doc.modelspace()
    source_cube = source_msp[0]
    assert isinstance(source_cube, Solid3d)

    ezdxf.xref.load_modelspace(source_doc, target_doc)

    target_msp = target_doc.modelspace()
    loaded_cube = target_msp[0]
    assert isinstance(loaded_cube, Solid3d)
    assert loaded_cube.sat == source_cube.sat


def test_load_acis_from_R2013():
    target_doc = ezdxf.new("R2013")
    source_doc = source_doc_R2013()
    source_msp = source_doc.modelspace()
    source_cube = source_msp[0]
    assert isinstance(source_cube, Solid3d)

    ezdxf.xref.load_modelspace(source_doc, target_doc)

    target_msp = target_doc.modelspace()
    loaded_cube = target_msp[0]
    assert isinstance(loaded_cube, Solid3d)
    sab = loaded_cube.sab
    assert len(sab) > 1
    assert sab == source_cube.sab


def test_load_acis_from_2007_into_2013():
    target_doc = ezdxf.new("R2013")  # SAB

    source_doc = source_doc_R2007()
    ezdxf.xref.load_modelspace(source_doc, target_doc)

    target_msp = target_doc.modelspace()
    loaded_cube = target_msp[0]
    assert isinstance(loaded_cube, Solid3d)
    assert len(loaded_cube.sat) == 0, "SAT data removed"
    assert len(loaded_cube.sab) == 0


def test_load_acis_from_2013_into_2007():
    target_doc = ezdxf.new("R2007")  # SAT

    source_doc = source_doc_R2013()
    ezdxf.xref.load_modelspace(source_doc, target_doc)

    target_msp = target_doc.modelspace()
    loaded_cube = target_msp[0]
    assert isinstance(loaded_cube, Solid3d)
    assert len(loaded_cube.sat) == 0
    assert len(loaded_cube.sab) == 0, "SAB data removed"


if __name__ == "__main__":
    pytest.main([__file__])

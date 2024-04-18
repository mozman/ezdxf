# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.document import Drawing
from ezdxf.math import Matrix44
from ezdxf.render.forms import cube
from ezdxf.acis.api import body_from_mesh, export_sab

FILENAME = "3dsolid.dxf"


@pytest.fixture
def doc():
    acis_body = body_from_mesh(cube())
    _doc = ezdxf.new()
    msp = _doc.modelspace()
    dxf_3dsolid = msp.add_3dsolid()
    dxf_3dsolid.sab = export_sab([acis_body])
    dxf_3dsolid.transform(Matrix44.translate(10, 11, 12))
    return _doc


def test_apply_transformations_to_acis_entities(doc: Drawing):
    # this is done automatically when exporting the DXF document
    try:
        doc.commit_pending_changes()
    except Exception as e:
        pytest.fail(f"commit_pending_changes() raises unexpected exception: {str(e)}")


def test_export_and_reload_transformed_acis_entities(tmp_path, doc: Drawing):
    file_path = tmp_path / FILENAME
    doc.saveas(file_path)
    del doc

    doc2 = ezdxf.readfile(file_path)
    # Do not test the current implementation, this may change in the future:
    solids = doc2.query("3DSOLID")
    assert len(solids) == 1

    dxf_3dsolid = solids[0]
    assert len(dxf_3dsolid.sab) > 16


if __name__ == "__main__":
    pytest.main([__file__])

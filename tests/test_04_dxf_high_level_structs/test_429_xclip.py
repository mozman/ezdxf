# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.document import Drawing
from ezdxf.entities import factory, Dictionary, XRecord
from ezdxf import xclip
from ezdxf.math import BoundingBox2d
from ezdxf.entities.acad_xrec_roundtrip import RoundtripXRecord

TEST_BLK = "TEST_BLK"


@pytest.fixture(scope="module")
def doc() -> Drawing:
    _doc = ezdxf.new()
    blk = _doc.blocks.new(TEST_BLK)
    blk.add_line((0, 0), (10, 10))
    return _doc


@pytest.fixture
def clipper(doc: Drawing) -> xclip.XClip:
    msp = doc.modelspace()
    insert = msp.add_blockref(TEST_BLK, (10, 10))
    return xclip.XClip(insert)


def test_new_clipping_path_dxf_structure(doc: Drawing):
    msp = doc.modelspace()
    insert = msp.add_blockref(TEST_BLK, (10, 10))
    clipper = xclip.XClip(insert)
    clipper.set_block_clipping_path([(-1, -1), (2, 2)])

    spatial_filter = clipper.get_spatial_filter()
    assert spatial_filter is not None
    assert factory.is_bound(spatial_filter, doc) is True

    acad_filter_dict = doc.entitydb.get(spatial_filter.dxf.owner)
    assert isinstance(acad_filter_dict, Dictionary)
    assert acad_filter_dict.get("SPATIAL") is spatial_filter

    assert spatial_filter.reactors is not None
    assert acad_filter_dict.dxf.handle in spatial_filter.reactors

    xdict = insert.get_extension_dict()
    assert xdict["ACAD_FILTER"] is acad_filter_dict

    assert spatial_filter in doc.objects


def test_new_clipping_path_geometry(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(-2, -1), (2, -1), (0, 2)])
    clipping_path = clipper.get_block_clipping_path()

    assert len(clipping_path.vertices) == 3
    assert len(clipping_path.inverted_clip) == 0
    assert clipping_path.is_inverted_clip is False


@pytest.mark.parametrize("vertices", [[], [(0, 0)]])
def test_invalid_clipping_path_raises_exception(clipper: xclip.XClip, vertices):
    with pytest.raises(ValueError):
        clipper.set_block_clipping_path(vertices)


def test_rectangular_clipping_path_geometry(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(-1, 2), (2, -1)])
    clipping_path = clipper.get_block_clipping_path()
    # counter-clockwise rectangular boundary path
    p0, p1, p2, p3 = clipping_path.vertices
    assert p0.isclose((-1, -1)) is True
    assert p1.isclose((2, -1)) is True
    assert p2.isclose((2, 2)) is True
    assert p3.isclose((-1, 2)) is True


def test_new_spatial_filter_parmeters(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(-1, -1), (2, 2)])
    assert clipper.is_clipping_enabled is True
    assert clipper.has_clipping_path is True

    spatial_filter = clipper.get_spatial_filter()
    assert spatial_filter.dxf.has_front_clipping_plane == 0
    assert spatial_filter.dxf.front_clipping_plane_distance == 0.0
    assert spatial_filter.dxf.has_back_clipping_plane == 0
    assert spatial_filter.dxf.back_clipping_plane_distance == 0.0
    assert spatial_filter.dxf.origin == (0, 0, 0)
    assert spatial_filter.dxf.extrusion == (0, 0, 1)


def test_enable_clipping_without_path_set(clipper: xclip.XClip):
    clipper.enable_clipping()
    assert clipper.is_clipping_enabled is False
    clipper.disable_clipping()
    assert clipper.is_clipping_enabled is False


def test_toggle_clipping_state(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(0, 0), (1, 1)])
    assert clipper.is_clipping_enabled is True, "clipping path is enabled by default"

    clipper.disable_clipping()
    assert clipper.is_clipping_enabled is False

    clipper.enable_clipping()
    assert clipper.is_clipping_enabled is True


def test_discard_clipping_path(doc: Drawing):
    msp = doc.modelspace()
    insert = msp.add_blockref(TEST_BLK, (10, 10))
    clipper = xclip.XClip(insert)

    clipper.set_block_clipping_path([(0, 0), (1, 1)])
    spatial_filter = clipper.get_spatial_filter()

    clipper.discard_clipping_path()
    assert clipper.has_clipping_path is False
    assert spatial_filter.is_alive is False, "destroy SPATIAL_FILTER entity"
    assert insert.has_extension_dict is True, "do not discard empty extension dict"
    assert spatial_filter not in doc.objects, "removed from objects section"


def test_cleanup_base_entity(clipper: xclip.XClip):
    insert = clipper._insert
    clipper.set_block_clipping_path([(0, 0), (1, 1)])

    clipper.cleanup()
    assert insert.has_extension_dict is True, "do not discard non-empty extension dict"

    clipper.discard_clipping_path()
    assert (
        insert.has_extension_dict is True
    ), "do not discard empty extension dict automatically"

    clipper.cleanup()
    assert insert.has_extension_dict is False, "discard empty extension dict"


def test_get_wcs_clipping_path(doc: Drawing):
    """The clipping path defined in BLOCK coordinates should be transformed to the
    location of the INSERT entity.
    """
    msp = doc.modelspace()
    insert = msp.add_blockref(TEST_BLK, (10, 10))
    clipper = xclip.XClip(insert)

    clipper.set_block_clipping_path([(0, 0), (1, 1)])
    clipping_path = clipper.get_wcs_clipping_path()
    bbox = BoundingBox2d(clipping_path.vertices)
    assert bbox.extmin.isclose((10, 10))
    assert bbox.extmax.isclose((11, 11))


def test_set_wcs_clipping_path(doc: Drawing):
    """The clipping path defined in WCS coordinates should be stored as BLOCK
    coordinates.
    """
    msp = doc.modelspace()
    insert = msp.add_blockref(TEST_BLK, (10, 10))
    clipper = xclip.XClip(insert)

    clipper.set_wcs_clipping_path([(10, 10), (11, 11)])
    clipping_path = clipper.get_block_clipping_path()
    bbox = BoundingBox2d(clipping_path.vertices)
    assert bbox.extmin.isclose((0, 0))
    assert bbox.extmax.isclose((1, 1))


def test_invert_clip_without_clipping_path(clipper: xclip.XClip):
    with pytest.raises(ValueError):
        clipper.invert_clipping_path(ignore_acad_compatibility=True)


def test_cannot_invert_clipping_path_twice(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(2, 2), (8, 8)])
    clipper.invert_clipping_path(ignore_acad_compatibility=True)

    with pytest.raises(ValueError):
        clipper.invert_clipping_path(ignore_acad_compatibility=True)


def test_invert_clipping_path_properties(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(2, 2), (8, 8)])
    clipper.invert_clipping_path(ignore_acad_compatibility=True)

    assert clipper.is_inverted_clip is True
    clipping_path = clipper.get_block_clipping_path()

    assert clipping_path.is_inverted_clip is True
    # the inner clipping path - "The Hole"
    bbox = BoundingBox2d(clipping_path.inverted_clip)
    assert bbox.extmin.isclose((2, 2))
    assert bbox.extmax.isclose((8, 8))

    bbox = BoundingBox2d(clipping_path.vertices)
    # outer boundary is extents of block content + 10%
    # block content = Line((0, 0), (10, 10))
    assert bbox.extmin.isclose((-1, -1))
    assert bbox.extmax.isclose((11, 11))


def test_invert_clipping_path_dxf_structure(clipper: xclip.XClip):
    clipper.set_block_clipping_path([(2, 2), (8, 8)])
    clipper.invert_clipping_path(ignore_acad_compatibility=True)

    spatial_filter = clipper.get_spatial_filter()
    assert spatial_filter is not None
    xdict = spatial_filter.get_extension_dict()
    xrec = xdict["ACAD_XREC_ROUNDTRIP"]
    assert isinstance(xrec, XRecord) is True

    rtr = RoundtripXRecord(xrec)
    assert len(rtr.get_section("ACAD_INVERTEDCLIP_ROUNDTRIP")) == 4
    assert len(rtr.get_section("ACAD_INVERTEDCLIP_ROUNDTRIP_COMPARE")) == 11


if __name__ == "__main__":
    pytest.main([__file__])

# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.entities.spatial_filter import SpatialFilter


def test_setup_from_tags():
    sp_filter = SpatialFilter.from_text(SPATIAL_FILTER_0)
    assert len(sp_filter.boundary_vertices) == 2
    assert sp_filter.dxf.extrusion == (0, 0, 1)
    assert sp_filter.dxf.origin == (0, 0, 0)
    assert sp_filter.dxf.display_clipping_path == 1
    assert sp_filter.dxf.has_front_clipping_plane == 0
    assert sp_filter.dxf.front_clipping_plane_distance == 0.0
    assert sp_filter.dxf.has_back_clipping_plane == 0
    assert sp_filter.dxf.back_clipping_plane_distance == 0.0

def test_loaded_transform_matrix():
    sp_filter = SpatialFilter.from_text(SPATIAL_FILTER_0)
    m = sp_filter.transform_matrix
    assert m.get_row(0) == (1, 0, 0, 0)
    assert m.get_row(1) == (0, 1, 0, 0)
    assert m.get_row(2) == (0, 0, 1, 0)
    assert m.get_row(3) == (0, 0, 0, 1)

def test_loaded_inverse_insert_matrix():
    sp_filter = SpatialFilter.from_text(SPATIAL_FILTER_0)
    m = sp_filter.inverse_insert_matrix
    assert m.get_row(0) == (1, 0, 0, 0)
    assert m.get_row(1) == (0, 1, 0, 0)
    assert m.get_row(2) == (0, 0, 1, 0)
    assert m.get_row(3) == (-240.0, -165.0, 0, 1)

def test_dxf_export():
    sp_filter = SpatialFilter.from_text(SPATIAL_FILTER_0)
    tag_collector = TagCollector()
    sp_filter.export_dxf(tag_collector)
    expected_tags = basic_tags_from_text(SPATIAL_FILTER_0)
    for tag, expected in zip(tag_collector.tags, expected_tags):
        assert tag == expected


SPATIAL_FILTER_0 = """  0
SPATIAL_FILTER
  5
A7
102
{ACAD_REACTORS
330
A6
102
}
330
A6
100
AcDbFilter
100
AcDbSpatialFilter
 70
  2
 10
220.2
 20
152.1
 10
270.1
 20
206.8
210
0.0
220
0.0
230
1.0
 11
0.0
 21
0.0
 31
0.0
 71
  1
 72
  0
 73
  0
 40
1.0
 40
0.0
 40
0.0
 40
-240.0
 40
0.0
 40
1.0
 40
0.0
 40
-165.0
 40
0.0
 40
0.0
 40
1.0
 40
0.0
 40
1.0
 40
0.0
 40
0.0
 40
0.0
 40
0.0
 40
1.0
 40
0.0
 40
0.0
 40
0.0
 40
0.0
 40
1.0
 40
0.0
"""

if __name__ == "__main__":
    pytest.main([__file__])

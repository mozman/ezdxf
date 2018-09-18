# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.modern.geodata import GeoData


@pytest.fixture
def geodata():
    return GeoData(ExtendedTags.from_text(GEODATA))


def test_geodata_dxf_attributes(geodata):
    assert geodata.dxf.handle == 'F658'
    assert geodata.has_reactors() is True
    assert geodata.dxf.version == 3
    assert geodata.dxf.block_record == '70'
    assert geodata.dxf.design_point == (-7000, -1000, 0)
    assert geodata.dxf.reference_point == (14, 48, 0)
    assert geodata.dxf.north_direction == (.13, .99)
    assert geodata.dxf.horizontal_unit_scale == 1.
    assert geodata.dxf.vertical_unit_scale == 1.
    assert geodata.dxf.horizontal_units == 6
    assert geodata.dxf.vertical_units == 6
    assert geodata.dxf.up_direction == (0, 0, 1)
    assert geodata.dxf.scale_estimation_method == 3
    assert geodata.dxf.sea_level_correction == 0
    assert geodata.dxf.user_scale_factor == 1
    assert geodata.dxf.sea_level_elevation == 0
    assert geodata.dxf.coordinate_projection_radius == 0
    assert geodata.dxf.geo_rss_tag == 'DUMMY_TAG'
    assert geodata.dxf.observation_from_tag == 'DUMMY_OFT'
    assert geodata.dxf.observation_to_tag == 'DUMMY_OTT'
    assert geodata.dxf.mesh_point_count == 4


def test_geodata_get_mesh_data(geodata):
    vertices, faces = geodata.get_mesh_data()
    assert len(vertices) == geodata.dxf.mesh_point_count
    assert len(faces) == 0


def test_geodata_delete_mesh_data(geodata):
    geodata.set_mesh_data()
    assert geodata.dxf.mesh_point_count == 0
    assert geodata.dxf.mesh_faces_count == 0


def test_geodata_set_get_mesh_data(geodata):
    # vertex structure
    # [(source vertex, target_vertex), ...]
    vertices = [
        ((1, 1), (2, 2)),
        ((3, 3), (4, 4)),
        ((5, 5), (6, 6)),
    ]
    faces = [[0, 1, 2]]
    geodata.set_mesh_data(vertices, faces)
    assert geodata.dxf.mesh_point_count == 3
    assert geodata.dxf.mesh_faces_count == 1

    vertices2, faces2 = geodata.get_mesh_data()
    assert vertices == vertices2
    assert faces == faces2


TEST_TEXT = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore 
magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd 
gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing 
elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero 
eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum 
dolor sit amet.
"""


def test_geodata_coordinate_system_definition(geodata):
    assert geodata.get_coordinate_system_definition() == 'Text0Text1'

    geodata.set_coordinate_system_definition(TEST_TEXT)
    assert geodata.get_coordinate_system_definition() == TEST_TEXT


def test_internals_set_geodata_coordinate_system_definition_(geodata):
    # in this case internal structure testing is required
    geodata.AcDbGeoData.remove_tags((301, 303))  # delete existing text
    assert geodata.get_coordinate_system_definition() == ''

    with pytest.raises(ezdxf.DXFValueError):
        geodata.AcDbGeoData.tag_index(301)

    # all 301 and 303 tags are removed
    geodata.set_coordinate_system_definition(TEST_TEXT)
    # Not tested if AutoCAD accepts the new position of 301 and 303 tags, but according to the DXF reference tag order
    # should not matter!
    assert geodata.get_coordinate_system_definition() == TEST_TEXT


def test_create_new_geo_data_for_model_space():
    dwg = ezdxf.new('R2010')
    msp = dwg.modelspace()
    assert msp.get_geodata() is None
    geodata = msp.new_geodata()
    assert geodata.dxftype() == 'GEODATA'


GEODATA = """  0
GEODATA
5
F658
102
{ACAD_REACTORS
330
803A
102
}
330
803A
100
AcDbGeoData
90
3
330
70
70
2
10
-7000
20
-1000
30
0.0
11
14.
21
48.
31
0.0
40
1.0
91
6
41
1.0
92
6
210
0.0
220
0.0
230
1.0
12
0.13
22
0.99
95
3
141
1.0
294
0
142
0.0
143
0.0
303
Text0
301
Text1
302
DUMMY_TAG
305
DUMMY_OFT
306
DUMMY_OTT
307

93
4
13
-596044.3104449062
23
-1966225.111236282
14
17.66571737167506
24
42.00025909173485
13
1403002.41871386
23
-1966225.111236282
14
41.46357474182291
24
40.89934076070281
13
1403002.41871386
23
-339583.1428681399
14
46.99412402090528
24
55.00032933828663
13
-596044.3104449062
23
-337956.5008997718
14
15.23395535970868
24
56.52797613716202
96
0
"""

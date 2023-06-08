#  Copyright (c) 2020-2021, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
import copy
from ezdxf.math import Vec3, Matrix44
from ezdxf.entities import (
    factory,
    Hatch,
    MPolygon,
    LWPolyline,
    BoundaryPathType,
)
from ezdxf.entities.polygon import DXFPolygon
from ezdxf.addons import geo
from ezdxf.render.forms import square, translate

EXTERIOR = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
HOLE1 = [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]
HOLE2 = [(3, 3), (3, 4), (4, 4), (4, 3), (3, 3)]

POINT = {"type": "Point", "coordinates": (0, 0)}
LINE_STRING = {"type": "LineString", "coordinates": EXTERIOR}
POLYGON_0 = {"type": "Polygon", "coordinates": [EXTERIOR]}
POLYGON_1 = {"type": "Polygon", "coordinates": [EXTERIOR, HOLE1]}
POLYGON_2 = {"type": "Polygon", "coordinates": [EXTERIOR, HOLE1, HOLE2]}
MULTI_POINT = {
    "type": "MultiPoint",
    "coordinates": EXTERIOR,
}
MULTI_LINE_STRING = {
    "type": "MultiLineString",
    "coordinates": [EXTERIOR, HOLE1, HOLE2],
}
MULTI_POLYGON = {
    "type": "MultiPolygon",
    "coordinates": [
        [EXTERIOR],
        [EXTERIOR, HOLE1],
        [EXTERIOR, HOLE1, HOLE2],
    ],
}

GEOMETRY_COLLECTION = {
    "type": "GeometryCollection",
    "geometries": [
        POINT,
        LINE_STRING,
        POLYGON_0,
    ],
}
FEATURE_1 = {
    "type": "Feature",
    "prop0": "property",
    "geometry": LINE_STRING,
}
FEATURE_2 = {
    "type": "Feature",
    "prop0": "property",
    "geometry": LINE_STRING,
}

FEATURE_COLLECTION = {
    "type": "FeatureCollection",
    "features": [FEATURE_1, FEATURE_2],
}

FEATURE_PROPERTIES = {
    "type": "Feature",
    "properties": {"layer": "GeoJSON"},
    "geometry": LINE_STRING,
}

FEATURE_PROPERTIES_GC = {
    "type": "Feature",
    "properties": {"layer": "GeoJSON"},
    "geometry": GEOMETRY_COLLECTION,
}


@pytest.mark.parametrize(
    "points",
    [
        [],
        [(0, 0)],
        [(0, 0), (1, 0)],
    ],
)
def test_polygon_mapping_vertex_count_error(points):
    with pytest.raises(ValueError):
        geo.polygon_mapping(Vec3.list(points), [])


def test_map_dxf_point():
    point = factory.new("POINT", dxfattribs={"location": (0, 0)})
    assert geo.mapping(point) == {"type": "Point", "coordinates": (0, 0)}


def test_map_dxf_line():
    point = factory.new("LINE", dxfattribs={"start": (0, 0), "end": (1, 0)})
    assert geo.mapping(point) == {
        "type": "LineString",
        "coordinates": [(0, 0), (1, 0)],
    }


def test_map_polyline():
    pline = cast("Polyline", factory.new("POLYLINE"))
    pline.append_vertices([(0, 0), (1, 0), (1, 1)])
    pline.close()
    assert geo.mapping(pline) == {
        "type": "Polygon",
        "coordinates": ([(0, 0), (1, 0), (1, 1), (0, 0)], []),
    }
    assert geo.mapping(pline, force_line_string=True) == {
        "type": "LineString",
        "coordinates": [(0, 0), (1, 0), (1, 1), (0, 0)],
    }


@pytest.mark.parametrize("dxftype", ["HATCH", "MPOLYGON"])
def test_map_dxf_polygon(dxftype: str):
    hatch = cast(
        Hatch,
        factory.new(
            dxftype,
            dxfattribs={
                "hatch_style": 0,
            },
        ),
    )
    hatch.paths.add_polyline_path(EXTERIOR, flags=1)  # EXTERNAL
    hatch.paths.add_polyline_path(HOLE1, flags=0)  # DEFAULT
    hatch.paths.add_polyline_path(HOLE2, flags=0)  # DEFAULT
    m = geo.mapping(hatch)
    assert m["type"] == "Polygon"
    exterior, holes = m["coordinates"]
    assert len(exterior) == 5  # vertices
    assert len(holes) == 2
    assert len(holes[0]) == 5  # vertices
    assert len(holes[1]) == 5  # vertices


def test_map_circle():
    circle = factory.new("CIRCLE")
    m = geo.mapping(circle)
    assert m["type"] == "Polygon"
    assert len(m["coordinates"][0]) == 8
    m = geo.mapping(circle, force_line_string=True)
    assert m["type"] == "LineString"


def test_map_arc():
    arc = factory.new(
        "ARC",
        dxfattribs={
            "start_angle": 0,
            "end_angle": 90,
        },
    )
    m = geo.mapping(arc)
    assert m["type"] == "LineString"
    assert len(m["coordinates"][0]) > 1


def test_arc_geo_proxy_wcs_to_crs():
    arc = factory.new(
        "ARC",
        dxfattribs={
            "start_angle": 0,
            "end_angle": 90,
        },
    )
    geo_proxy = geo.proxy(arc)
    geo_proxy.wcs_to_crs(Matrix44())
    assert len(geo_proxy.__geo_interface__["coordinates"][0]) > 1


@pytest.mark.parametrize(
    "entity",
    [
        {"type": "Point", "coordinates": (0, 0)},
        {"type": "LineString", "coordinates": [(0, 0), (1, 0)]},
        {"type": "MultiPoint", "coordinates": [(0, 0), (1, 0)]},
        {
            "type": "MultiLineString",
            "coordinates": [[(0, 0), (1, 0)], [(0, 0), (1, 0)]],
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": (0, 0)},
        },
        {
            "type": "GeometryCollection",
            "geometries": [{"type": "Point", "coordinates": (0, 0)}],
        },
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": (0, 0)},
                }
            ],
        },
    ],
)
def test_parse_types(entity):
    # Parser does basic structure validation and converts all coordinates into
    # Vec3 objects.
    assert geo.parse(entity) == entity


def test_parsing_type_error():
    with pytest.raises(TypeError):
        geo.parse({"type": "XXX"})


@pytest.mark.parametrize(
    "entity",
    [
        {"type": "Point"},  # no coordinates key
        {"type": "Point", "coordinates": None},  # no coordinates
        {"type": "Feature"},  # no geometry key
        {"type": "GeometryCollection"},  # no geometries key
        {"type": "FeatureCollection"},  # no features key
    ],
)
def test_parsing_value_error(entity):
    with pytest.raises(ValueError):
        geo.parse(entity)


def test_parse_polygon_without_holes():
    polygon = geo.parse(POLYGON_0)
    assert polygon["coordinates"] == (EXTERIOR, [])


def test_parse_polygon_1_hole():
    polygon = geo.parse(POLYGON_1)
    assert polygon["coordinates"] == (EXTERIOR, [HOLE1])


def test_parse_polygon_2_holes():
    polygon = geo.parse(POLYGON_2)
    assert polygon["coordinates"] == (EXTERIOR, [HOLE1, HOLE2])


def test_parse_geometry_collection():
    geometry_collection = geo.parse(GEOMETRY_COLLECTION)
    assert len(geometry_collection["geometries"]) == 3


def test_parse_feature():
    feature = geo.parse(FEATURE_1)
    assert feature["geometry"] == LINE_STRING


def test_feature_with_geometry_collection():
    feature = geo.parse(FEATURE_PROPERTIES_GC)
    geometry_collection = feature["geometry"]
    assert geometry_collection["type"] == "GeometryCollection"
    geometries = geometry_collection["geometries"]
    assert isinstance(geometries, list)


def test_parse_feature_collection():
    feature_collection = geo.parse(FEATURE_COLLECTION)
    assert len(feature_collection["features"]) == 2


def test_iter_feature_with_geometry_collection():
    gp = geo.GeoProxy(FEATURE_PROPERTIES_GC)
    entities = list(gp)
    assert len(entities) == 3


@pytest.mark.parametrize(
    "entity",
    [
        POINT,
        LINE_STRING,
        POLYGON_0,
        POLYGON_1,
        POLYGON_2,
        GEOMETRY_COLLECTION,
        FEATURE_1,
        FEATURE_COLLECTION,
        MULTI_POINT,
        MULTI_LINE_STRING,
        MULTI_POLYGON,
    ],
)
def test_geo_interface_builder(entity):
    assert geo.GeoProxy.parse(entity).__geo_interface__ == entity


def test_point_to_dxf_entity():
    point = list(geo.dxf_entities(POINT))[0]
    assert point.dxftype() == "POINT"
    assert point.dxf.location == (0, 0)


def test_line_string_to_dxf_entity():
    res = cast(LWPolyline, list(geo.dxf_entities(LINE_STRING))[0])
    assert res.dxftype() == "LWPOLYLINE"
    assert list(res.vertices()) == Vec3.list(EXTERIOR)


@pytest.mark.parametrize("dxftype, polygon", [("HATCH", 1), ("MPOLYGON", 4)])
def test_polygon_without_holes_to_dxf_polygon(dxftype, polygon):
    entity = cast(DXFPolygon, list(geo.dxf_entities(POLYGON_0, polygon=polygon))[0])
    assert entity.dxftype() == dxftype
    assert len(entity.paths) == 1
    p = entity.paths[0]
    assert p.type == BoundaryPathType.POLYLINE
    assert p.vertices == Vec3.list(EXTERIOR)


@pytest.mark.parametrize("dxftype, polygon", [("HATCH", 1), ("MPOLYGON", 4)])
def test_polygon_with_holes_to_dxf_polygon(dxftype, polygon):
    entity = cast(DXFPolygon, list(geo.dxf_entities(POLYGON_2, polygon=polygon))[0])
    assert entity.dxftype() == dxftype
    assert len(entity.paths) == 3
    p = entity.paths[1]
    assert p.type == BoundaryPathType.POLYLINE
    assert p.vertices == Vec3.list(HOLE1)
    p = entity.paths[2]
    assert p.type == BoundaryPathType.POLYLINE
    assert p.vertices == Vec3.list(HOLE2)


def test_mpolygon_supports_fill_and_border_color():
    attribs = {"color": 2, "fill_color": 3}
    mpolygon = cast(
        MPolygon,
        list(geo.dxf_entities(POLYGON_2, polygon=4, dxfattribs=attribs))[0],
    )
    assert mpolygon.dxftype() == "MPOLYGON"
    assert mpolygon.dxf.color == 2
    assert mpolygon.dxf.fill_color == 3


def test_geometry_collection_to_dxf_entities():
    collection = list(geo.dxf_entities(GEOMETRY_COLLECTION))
    assert len(collection) == 3


def test_feature_to_dxf_entities():
    entities = list(geo.dxf_entities(FEATURE_1))
    assert entities[0].dxftype() == "LWPOLYLINE"


def test_feature_collection_to_dxf_entities():
    collection = list(geo.dxf_entities(FEATURE_COLLECTION))
    assert len(collection) == 2
    assert collection[0].dxftype() == "LWPOLYLINE"


def test_dxf_entities_post_process_properties():
    entities = list(
        geo.dxf_entities(FEATURE_PROPERTIES, post_process=geo.assign_layers)
    )
    polyline = entities[0]
    assert polyline.dxf.layer == "GeoJSON"


def test_dxf_entities_from_geometry_collection_post_process_properties():
    entities = list(
        geo.dxf_entities(FEATURE_PROPERTIES_GC, post_process=geo.assign_layers)
    )
    assert len(entities) == 3
    for e in entities:
        assert e.dxf.layer == "GeoJSON"


@pytest.mark.parametrize(
    "deg, coords",
    [
        [(15, 47), (1669792.36, 5910809.62)],
        [(-15, 47), (-1669792.36, 5910809.62)],
        [(15, -47), (1669792.36, -5910809.62)],
        [(-15, -47), (-1669792.36, -5910809.62)],
        [(0, 0), (0, 0)],
    ],
)
def test_common_WGS84_projection(deg, coords):
    projected = geo.wgs84_4326_to_3395(Vec3(deg))
    assert projected.round(2).isclose(coords)
    # inverse projection
    assert geo.wgs84_3395_to_4326(projected).isclose(deg)


def validate(p: geo.GeoProxy):
    return p.geotype == "Point"


@pytest.mark.parametrize(
    "entity,type_",
    [
        [POINT, "Point"],
        [LINE_STRING, None],
        [POLYGON_0, None],
        [MULTI_POINT, "MultiPoint"],
        [MULTI_LINE_STRING, None],
        [MULTI_POLYGON, None],
        [FEATURE_1, None],
    ],
)
def test_filter_function_single_entity(entity, type_):
    p = geo.GeoProxy(copy.deepcopy(entity))
    p.filter(validate)
    assert p.geotype == type_


def test_filter_function_geometrie_collection():
    p = geo.GeoProxy(copy.deepcopy(GEOMETRY_COLLECTION))
    p.filter(validate)
    assert p.geotype == "GeometryCollection"
    assert p.root["geometries"] == [POINT]

    gc2 = copy.deepcopy(GEOMETRY_COLLECTION)
    gc2["geometries"] = [LINE_STRING, POLYGON_0]
    p = geo.GeoProxy(gc2)
    p.filter(validate)
    assert p.geotype is None


def test_filter_function_feature_collection():
    fc1 = copy.deepcopy(FEATURE_COLLECTION)
    point_feature = copy.deepcopy(FEATURE_1)
    point_feature["geometry"] = POINT
    fc1["features"].append(point_feature)
    p = geo.GeoProxy(fc1)
    p.filter(validate)
    assert p.geotype == "FeatureCollection"
    assert p.root["features"] == [point_feature]

    p = geo.GeoProxy(copy.deepcopy(FEATURE_COLLECTION))
    p.filter(validate)
    assert p.geotype is None


def test_polygon_from_hatch_hole_in_hole():
    hatch = factory.new("HATCH")
    paths = hatch.paths
    paths.add_polyline_path(square(10), flags=1)
    paths.add_polyline_path(translate(square(8), (1, 1)), flags=0)
    paths.add_polyline_path(translate(square(6), (2, 2)), flags=0)
    mapping = geo.proxy(hatch).__geo_interface__
    assert mapping["type"] == "Polygon"
    assert len(mapping["coordinates"]) == 2, "inner hole should be removed"

    mapping = geo.proxy(hatch, force_line_string=True).__geo_interface__
    assert mapping["type"] == "MultiLineString"
    assert len(mapping["coordinates"]) == 3, "inner hole should not be removed"


def test_three_polygons_from_one_hatch():
    hatch = factory.new("HATCH")
    paths = hatch.paths
    paths.add_polyline_path(square(1), flags=1)
    paths.add_polyline_path(translate(square(1), (3, 1)), flags=1)
    paths.add_polyline_path(translate(square(1), (6, 2)), flags=1)
    mapping = geo.proxy(hatch).__geo_interface__
    assert mapping["type"] == "MultiPolygon"
    assert len(mapping["coordinates"]) == 3


if __name__ == "__main__":
    pytest.main([__file__])

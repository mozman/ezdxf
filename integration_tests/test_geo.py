#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.entities import factory
from ezdxf.render.forms import square, translate
from ezdxf.lldxf import const
from ezdxf.addons import geo

shapely_geometry = pytest.importorskip("shapely.geometry")


def test_shapely_geo_interface():
    point = shapely_geometry.shape(
        {
            "type": "Point",
            "coordinates": (0, 0),
        }
    )
    assert (point.x, point.y) == (0, 0)


def validate(geo_proxy: geo.GeoProxy) -> bool:
    return shapely_geometry.shape(geo_proxy).is_valid


def test_resolved_hatch_with_intersecting_holes():
    hatch = factory.new("HATCH")
    paths = hatch.paths
    paths.add_polyline_path(square(10), flags=const.BOUNDARY_PATH_EXTERNAL)
    paths.add_polyline_path(
        translate(square(3), (1, 1)), flags=const.BOUNDARY_PATH_DEFAULT
    )
    paths.add_polyline_path(
        translate(square(3), (2, 2)), flags=const.BOUNDARY_PATH_DEFAULT
    )
    p = geo.proxy(hatch)
    # Overlapping holes already resolved by fast_bbox_detection()
    polygon = shapely_geometry.shape(p)
    assert polygon.is_valid is True

    p.filter(validate)
    assert p.root["type"] == "Polygon"
    assert len(p.root["coordinates"]) == 2


def test_valid_hatch():
    hatch = factory.new("HATCH")
    paths = hatch.paths
    paths.add_polyline_path(square(10), flags=const.BOUNDARY_PATH_EXTERNAL)
    paths.add_polyline_path(
        translate(square(3), (1, 1)), flags=const.BOUNDARY_PATH_DEFAULT
    )
    paths.add_polyline_path(
        translate(square(3), (5, 1)), flags=const.BOUNDARY_PATH_DEFAULT
    )
    p = geo.proxy(hatch)
    polygon = shapely_geometry.shape(p)
    assert polygon.is_valid is True

    p.filter(validate)
    assert p.root != {}


if __name__ == "__main__":
    pytest.main([__file__])

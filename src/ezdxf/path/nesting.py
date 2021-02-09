#  Copyright (c) 2020-2021, Manfred Moitzi
#  License: MIT License
"""
This module provides "nested Polygon" detection for multiple paths.

Terminology
-----------

exterior
    creates a filled area, has counter-clockwise (ccw) winding in matplotlib
    exterior := Path

hole
    creates an unfilled area, has clockwise winding (cw) in matplotlib,
    hole := Polygon

polygon
    list of nested paths:
    polygon without a hole: [path]
    polygon with 1 hole: [path, [path]]
    polygon with 2 separated holes: [path, [path], [path]]
    polygon with 2 nested holes: [path, [path, [path]]]

    polygon := [exterior, hole*]

The result is a list of polygons:

1 polygon returns: [[ext-path]]
2 separated polygons returns: [[ext-path], [ext-path, [hole-path]]]

A hole is just another polygon, for a correct visualisation in
matplotlib the winding of the nested paths have to follow the alternating
order ccw-cw-ccw-cw... :

[Exterior-ccw,
    [Hole-Exterior-cw,
        [Sub-Hole-ccw],
        [Sub-Hole-ccw],
    ],
    [Hole-Exterior-cw],
    [Hole-Exterior-cw],
]

The implementation has to do some expensive tests, like check if a path is
inside of another path or if paths do overlap. A goal is to reduce this costs
by using proxy objects:

Bounding Box Proxy
------------------

Use the bounding box, this is very fast but not accurate, but could handle
most of the real world scenarios, in the assumption that most HATCHES are
created from non-overlapping boundary paths.
Overlap detection and resolving is not possible.

Bounding Box Construction:
- Fast: use bounding box from control vertices
- Accurate: use bounding box from flattened curve

Inside Check:
- Fast: center point of the bounding box
- Slow: use all corner points of the bounding box


Convex Hull Proxy
-----------------

Use the convex hull of the path, this is more accurate but also
much slower. Overlap detection and resolving is not possible.

Convex Hull construction:
- Fast: use convex hull from control vertices
- Accurate: use convex hull from flattened curve

Inside Check:
- Fast: center point of convex hull
- Slow: use all points of the convex hull


Flattened Curve
---------------

Use the flattened curve vertices, this is the most accurate solution and also
the slowest. Overlap detection and resolving is possible: exterior is the
union of two overlapping paths, hole is the intersection of this two paths,
the hole vertices have to be subtracted from the exterior vertices.

Sort by Area
------------

It is not possible for a path to contain another path with a larger area.

"""
from typing import TypeVar, Tuple, Optional, List, Iterable
from collections import namedtuple
from .path import Path
from ezdxf.math import BoundingBox2d

__all__ = [
    "fast_bbox_detection", "winding_deconstruction", "group_paths",
    "flatten_polygons"
]

Exterior = Path
Polygon = TypeVar('Polygon')
Hole = Polygon
Polygon = Tuple[Exterior, Optional[List[Hole]]]
BoxStruct = namedtuple('BoxStruct', 'bbox, path')


def fast_bbox_detection(paths: Iterable[Path]) -> List[Polygon]:
    """ Create a nested polygon structure from iterable `paths`, using 2D
    bounding boxes as fast detection objects.

    """

    # Implements fast bounding box construction and fast inside check.
    def area(item: BoxStruct) -> float:
        width, height = item.bbox.size
        return width * height

    def separate(exterior: BoundingBox2d, candidates: List[BoxStruct]
                 ) -> Tuple[List[BoxStruct], List[BoxStruct]]:
        holes = []
        outside = []
        for candidate in candidates:
            # Fast inside check:
            (holes if exterior.inside(candidate.bbox.center)
             else outside).append(candidate)
        return holes, outside

    def polygon_structure(outside: List[BoxStruct]) -> List[List]:
        polygons = []
        while outside:
            exterior = outside.pop()  # path with largest area
            # Get holes inside of exterior and returns the remaining paths
            # outside of exterior:
            holes, outside = separate(exterior.bbox, outside)
            if holes:
                # build nested hole structure:
                # the largest hole could contain the smaller holes,
                # and so on ...
                holes = polygon_structure(holes)
            polygons.append([exterior, *holes])
        return polygons

    def as_nested_paths(polygons) -> List:
        return [
            polygon.path if isinstance(polygon, BoxStruct)
            else as_nested_paths(polygon)
            for polygon in polygons
        ]

    boxed_paths = [
        # Fast bounding box construction:
        BoxStruct(BoundingBox2d(path.control_vertices()), path)
        for path in paths if len(path)
    ]
    boxed_paths.sort(key=area)
    return as_nested_paths(polygon_structure(boxed_paths))


def winding_deconstruction(polygons: List[Polygon]
                           ) -> Tuple[List[Path], List[Path]]:
    """ Flatten the nested polygon structure in a tuple of two lists,
    the first list contains the paths which should be counter-clockwise oriented
    and the second list contains the paths which should be clockwise oriented.

    The paths are not converted to this orientation.

    """

    def deconstruct(polygons_, level):
        for polygon in polygons_:
            if isinstance(polygon, Path):
                # level 0 is the list of polygons
                # level 1 = ccw, 2 = cw, 3 = ccw, 4 = cw, ...
                (ccw_paths if (level % 2) else cw_paths).append(polygon)
            else:
                deconstruct(polygon, level + 1)

    cw_paths = []
    ccw_paths = []
    deconstruct(polygons, 0)
    return ccw_paths, cw_paths


def flatten_polygons(polygons: Polygon) -> Iterable[Path]:
    """ Yield a flat representation of the given nested polygons. """
    for polygon in polygons:
        if isinstance(polygon, Path):
            yield polygon
        else:
            yield from flatten_polygons(polygon)


def group_paths(paths: Iterable[Path]) -> List[List[Path]]:
    """ Group separated paths and their inner holes as flat lists. """
    polygons = fast_bbox_detection(paths)
    return [list(flatten_polygons(polygon)) for polygon in polygons]

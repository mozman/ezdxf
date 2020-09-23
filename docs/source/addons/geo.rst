.. _geo_addon:

.. module:: ezdxf.addons.geo

Geo Interface
=============

This module provides support for the  :code:`__geo_interface__`:
https://gist.github.com/sgillies/2217756

Which is also supported by `Shapely`_, for supported types see the `GeoJSON`_
Standard and examples in `Appendix-A`_.

The module can load ``__geo_interface__`` mappings as DXF entities by the
:func:`load` function from :class:`dict` like objects or Python objects with
``__geo_interface__`` support.

"Point" is loaded as :class:`~ezdxf.entities.Point` entity,  "LineString" is
loaded as :class:`~ezdxf.entities.LWPolyline` entity and "Polygon" is loaded as
:class:`~ezdxf.entities.Hatch` entity or as sparated
:class:`~ezdxf.entities.LWPolyline` entities (or both).
Loads geometries from"MultiPoint", "MultiLineString", "MultiPolygon",
"GeometryCollection", "Feature"  and from "FeatureCollection" objects.

The module creates ``__geo_interface__`` mappings by the :func:`mappings`
function or proxy objects with ``__geo_interface__`` support by the
:func:`proxy` function.

Supported DXF entities are:

- POINT as "Point"
- LINE as "LineString"
- LWPOLYLINE as "LineString" if open and "Polygon" if closed
- POLYLINE as "LineString" if open and "Polygon" if closed, supports only 2D and
  3D polylines, POLYMESH and POLYFACE are not supported
- SOLID, TRACE, 3DFACE as "Polygon"
- CIRCLE, ARC, ELLIPSE and SPLINE by approximation as "LineString" if open and
  "Polygon" if closed
- HATCH as "Polygon", holes are supported

.. warning::

    This module does no extensive validity checks for "Polygon" objects and
    because DXF has different requirements for HATCH boundary paths than the
    `GeoJSON`_ Standard, it is possible to create invalid "Polygon" objects.
    It is recommended to check critical objects by a sophisticated geometry
    library like `Shapely`_.

High Level Interface
--------------------

.. autofunction:: load(geo_mapping, polygon=1, dxfattribs: Dict = None, crs: Matrix44 = None) -> Iterable[DXFGraphic]

.. autofunction:: proxy(entity: Union[DXFGraphic, Iterable[DXFGraphic]], distance=0.1, force_line_string=False) -> GeoProxy

.. autofunction:: mapping(entity: DXFGraphic, distance=0.1, force_line_string=False) -> Dict

.. autofunction:: collection(entities: Iterable[DXFGraphic], distance=0.1, force_line_string=False) -> Dict

.. autofunction:: gfilter(entities: Iterable[DXFGraphic]) -> Iterable[DXFGraphic]

.. autofunction:: transform_wcs_to_crs

.. autofunction:: transform_crs_to_wcs


Low Level Interface
-------------------

.. autofunction:: mappings(entities: Iterable[DXFGraphic], distance=0.1, force_line_string=False) -> List[Dict]

.. autofunction:: point_mapping(point: Vertex) -> Dict

.. autofunction:: line_string_mapping(points: Iterable[Vertex]) -> Dict

.. autofunction:: polygon_mapping(points: Iterable[Vertex], holes: Iterable[Iterable[Vertex]] = None) -> Dict

.. autofunction:: join_multi_single_type_mappings

.. autofunction:: geometry_collection_mapping

.. autofunction:: linear_ring(points: Iterable[Vertex], ccw = True) -> List[Vector]

.. _Shapely: https://pypi.org/project/Shapely/

.. _GeoJSON: https://tools.ietf.org/html/rfc7946

.. _Appendix-A: https://tools.ietf.org/html/rfc7946#appendix-A
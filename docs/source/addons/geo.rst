.. _geo_addon:

.. module:: ezdxf.addons.geo

Geo Interface
=============

This module provides support for the  :code:`__geo_interface__`:
https://gist.github.com/sgillies/2217756

Which is also supported by `Shapely`_, for supported types see the `GeoJSON`_
Standard and examples in `Appendix-A`_.

Proxy From Mapping
------------------

The :class:`GeoProxy` represents a ``__geo_interface__`` mapping, create a new
proxy by :meth:`GeoProxy.parse` from an external ``__geo_interface__`` mapping.
:meth:`GeoProxy.to_dxf_entities` returns new DXF entities from this mapping.
Returns "Point" as :class:`~ezdxf.entities.Point` entity,  "LineString" as
:class:`~ezdxf.entities.LWPolyline` entity and "Polygon" as
:class:`~ezdxf.entities.Hatch` entity or as separated
:class:`~ezdxf.entities.LWPolyline` entities (or both).
Supports "MultiPoint", "MultiLineString", "MultiPolygon",
"GeometryCollection", "Feature"  and "FeatureCollection".
Add new DXF entities to a layout by the :meth:`Layout.add_entity` method.

Proxy From DXF Entity
---------------------

The :func:`proxy` function or the constructor :meth:`GeoProxy.from_dxf_entities`
creates a new :class:`GeoProxy` object from a single DXF entity or from an
iterable of DXF entities, entities without a coresponding representation will be
approximated.

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

Module Functions
----------------

.. autofunction:: proxy(entity: Union[DXFGraphic, Iterable[DXFGraphic]], distance=0.1, force_line_string=False) -> GeoProxy

.. autofunction:: dxf_entities(geo_mapping, polygon=1, dxfattribs: Dict = None) -> Iterable[DXFGraphic]

.. autofunction:: gfilter(entities: Iterable[DXFGraphic]) -> Iterable[DXFGraphic]

GeoProxy Class
--------------

.. autoclass:: GeoProxy

    .. autoattribute:: __geo_interface__

    .. automethod:: parse(geo_mapping: Dict) -> GeoProxy

    .. automethod:: from_dxf_entities(entity: Union[DXFGraphic, Iterable[DXFGraphic]], distance=0.1, force_line_string=False) -> GeoProxy

    .. automethod:: to_dxf_entities(polygon=1, dxfattribs: Dict = None) -> Iterable[DXFGraphic]

    .. automethod:: copy() -> GeoProxy

    .. automethod:: __iter__

    .. automethod:: wcs_to_crs

    .. automethod:: crs_to_wcs

.. _Shapely: https://pypi.org/project/Shapely/

.. _GeoJSON: https://tools.ietf.org/html/rfc7946

.. _Appendix-A: https://tools.ietf.org/html/rfc7946#appendix-A
.. _geo_addon:

.. module:: ezdxf.addons.geo

Geo Interface
=============

.. _geo_intended_usage:

Intended Usage
--------------

The intended usage of the :mod:`ezdxf.addons.geo` module is as tool to work with
geospatial data in conjunction with dedicated geospatial applications and
libraries and the module can not and should not replicate their functionality.

The only reimplemented feature is the most common WSG84 EPSG:3395 World
Mercator projection, for everything else use the dedicated packages like:

- `pyproj`_ - Cartographic projections and coordinate transformations library.
- `Shapely`_ - Manipulation and analysis of geometric objects in the Cartesian plane.
- `PyShp`_ - The Python Shapefile Library (PyShp) reads and writes ESRI Shapefiles in pure Python.
- `GeoJSON`_ - GeoJSON interface for Python.
- `GDAL`_ - Tools for programming and manipulating the GDAL Geospatial Data Abstraction Library.
- `Fiona`_ - Fiona is GDAL’s neat and nimble vector API for Python programmers.
- `QGIS`_ - A free and open source geographic information system.
- and many more ...

This module provides support for the  :code:`__geo_interface__`:
https://gist.github.com/sgillies/2217756

Which is also supported by `Shapely`_, for supported types see the `GeoJSON`_
Standard and examples in `Appendix-A`_.

.. seealso::

    :ref:`tut_geo_addon` for loading GPX data into DXF files with an existing
    geo location reference and exporting DXF entities as GeoJSON data.

Proxy From Mapping
------------------

The :class:`GeoProxy` represents a ``__geo_interface__`` mapping, create a new
proxy by :meth:`GeoProxy.parse` from an external ``__geo_interface__`` mapping.
:meth:`GeoProxy.to_dxf_entities` returns new DXF entities from this mapping.
Returns "Point" as :class:`~ezdxf.entities.Point` entity,  "LineString" as
:class:`~ezdxf.entities.LWPolyline` entity and "Polygon" as
:class:`~ezdxf.entities.Hatch` entity or as separated
:class:`~ezdxf.entities.LWPolyline` entities (or both) and new in v0.16.6 as
:class:`~ezdxf.entities.MPolygon`.
Supports "MultiPoint", "MultiLineString", "MultiPolygon",
"GeometryCollection", "Feature"  and "FeatureCollection".
Add new DXF entities to a layout by the :meth:`Layout.add_entity` method.

Proxy From DXF Entity
---------------------

The :func:`proxy` function or the constructor :meth:`GeoProxy.from_dxf_entities`
creates a new :class:`GeoProxy` object from a single DXF entity or from an
iterable of DXF entities, entities without a corresponding representation will be
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
- HATCH and MPOLYGON as "Polygon", holes are supported

.. versionadded:: 0.16.6

    MPOLYGON support

.. warning::

    This module does no extensive validity checks for "Polygon" objects and
    because DXF has different requirements for HATCH boundary paths than the
    `GeoJSON`_ Standard, it is possible to create invalid "Polygon" objects.
    It is recommended to check critical objects by a sophisticated geometry
    library like `Shapely`_.

Module Functions
----------------

.. autofunction:: proxy

.. autofunction:: dxf_entities

.. autofunction:: gfilter

GeoProxy Class
--------------

.. autoclass:: GeoProxy

    .. autoattribute:: __geo_interface__

    .. autoattribute:: geotype

    .. automethod:: parse(geo_mapping: Dict) -> GeoProxy

    .. automethod:: from_dxf_entities

    .. automethod:: to_dxf_entities

    .. automethod:: copy

    .. automethod:: __iter__

    .. automethod:: wcs_to_crs

    .. automethod:: crs_to_wcs

    .. automethod:: globe_to_map

    .. automethod:: map_to_globe

    .. automethod:: apply

    .. automethod:: filter

Helper Functions
----------------

.. autofunction:: wgs84_4326_to_3395

.. autofunction:: wgs84_3395_to_4326

.. autofunction:: dms2dd

.. autofunction:: dd2dms


.. _Appendix-A: https://tools.ietf.org/html/rfc7946#appendix-A
.. _pyproj: https://pypi.org/project/pyproj/
.. _Shapely: https://pypi.org/project/Shapely/
.. _PyShp: https://pypi.org/project/pyshp/
.. _GeoJSON: https://pypi.org/project/geojson/
.. _GDAL: https://pypi.org/project/gdal/
.. _Fiona: https://pypi.org/project/fiona/
.. _QGIS: https://www.qgis.org/en/site/

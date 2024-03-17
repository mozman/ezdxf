.. _tut_entity_selection:

Tutorial for Entity Selection
=============================

This tutorial shows how to use the :mod:`ezdxf.select` module, which provides functions 
to select entities based on various shapes.  These selection functions offer a way to 
filter entities based on their spatial location.

Why Bounding Boxes?
-------------------

The :mod:`~ezdxf.select` module primarily relies on bounding boxes to perform selections. 
Bounding boxes offer a fast way to identify potential overlaps between entities and the 
selection shape. This approach prioritizes performance over absolute accuracy.

Source of Entities
------------------

The source of the selection can be any iterable of DXF entities, like the modelspace, 
any paperspace layout or a block layout, also the result of an entity query as an 
:class:`~ezdxf.query.EntityQuery` container, or any collection of DXF entities that 
implements the :meth:`__iter__` method.

Selection Shapes
----------------

- :class:`~ezdxf.select.Window`: Defines a rectangular selection area.
- :class:`~ezdxf.select.Circle`: Selects entities within a circular area.
- :class:`~ezdxf.select.Polygon`: Selects entities based on the shape of a closed polygon.

Using Selection Functions
-------------------------

These selection functions utilize the selection shapes:

- :func:`~ezdxf.select.bbox_inside`: Selects entities whose bounding box lies withing the selection shape.
- :func:`~ezdxf.select.bbox_outside`: Selects entities whose bounding box is completely outside the selection shape.
- :func:`~ezdxf.select.bbox_overlap`: Selects entities whose bounding box overlaps the selection shape.

Additional selection functions:

- :func:`~ezdxf.select.bbox_chained`: Selects entities that are linked together by overlapping bounding boxes.
- :func:`~ezdxf.select.bbox_crosses_fence`: Selects entities whose bounding box overlaps an open polyline.
- :func:`~ezdxf.select.point_in_bbox`: Selects entities where the selection point lies within the bounding box.

The functions return an :class:`~ezdxf.query.EntityQuery` object, which provides access 
to the selected entities. You can iterate over the :class:`EntityQuery` to access each 
selected entity.

Bounding Box Inside Selection
-----------------------------

Selects entities which bounding boxes are completely within the selection shape.

Bounding Box Outside Selection
------------------------------

Selects entities whose bounding box is completely outside the selection shape.

Bounding Box Overlap Selection
------------------------------

Selects entities whose bounding box overlaps the selection shape.

This function works similar to the crossing selection in CAD applications, but not 
exactly the same.  The function selects entities whose bounding boxes overlap the 
selection shape.  This will also select elements where all of the entity geometry is 
outside the selection shape, but the bounding box overlaps the selection shape, 
e.g. border polylines.

Bounding Box Chained Selection
------------------------------

Selects elements that are directly or indirectly connected to each other by overlapping 
bounding boxes. The selection begins at the specified starting element.

Bounding Box Crosses Fence
--------------------------

Selects entities whose bounding box intersects an open polyline.

Point In Bounding Box Selection
-------------------------------

Selects entities where the selection point lies within the bounding box.


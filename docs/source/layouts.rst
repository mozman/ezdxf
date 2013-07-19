Layout
======

A Layout represents and manages drawing entities, there are three different
layout objects:

- Modelspace is the common working space, containing basic drawing entities.
- Paperspaces are arrangements of objects for printing and plotting,
  this layouts contains basic drawing entities and viewports to the model-space.
- BlockLayout works on an associated :class:`Block`, Blocks are
  collections of drawing entities for reusing by block references.

.. class:: Layout

Access existing drawing entities
--------------------------------

.. method:: Layout.__iter__()

   Iterate over all drawing entities in this layout.

.. method:: Layout.__contains__(entity)

   Test if the layout contains the drawing element `entity`.

.. method:: Layout.query(query='*')

   Get included DXF entities matching the :ref:`entity query string` *query*.
   Returns a sequence of type :class:`EntityQuery`.

Create new drawing entities
---------------------------

.. method:: Layout.add_line(start, end, dxfattribs=None)

   Add a :class:`Line` element, starting at 2D/3D point `start` and ending at
   the 2D/3D point `end`.

.. method:: Layout.add_circle(center, radius, dxfattribs=None)

   Add a :class:`Circle` element, `center` is 2D/3D point, `radius` in drawing
   units.

.. method:: Layout.add_arc(center, radius, start_angle, end_angle, dxfattribs=None)

   Add an :class:`Arc` element, `center` is 2D/3D point, `radius` in drawing
   units, `start_angle` and `end_angle` in degrees.

.. method:: Layout.add_solid(points, dxfattribs=None)

   Add a :class:`Solid` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_trace(points, dxfattribs=None)

   Add a :class:`Trace` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_3Dface(points, dxfattribs=None)

   Add a :class:`3DFace` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_text(text, dxfattribs=None)

   Add a :class:`Text` element, `text` is a string, see also :class:`Style`.

.. method:: Layout.add_blockref(name, insert, dxfattribs=None)

   Add an :class:`Insert` element, `name` is the block name, `insert` is a
   2D/3D point.

.. method:: Layout.add_auto_blockref(name, insert, values, dxfattribs=None)

   Add an :class:`Insert` element, `name` is the block name, `insert` is a
   2D/3D point. Add :class:`Attdef`, defined in the block definition,
   automatically as :class:`Attrib` to the block reference, and set text of
   :class:`Attrib`. `values` is a dict with key=tag, value=text values.

.. method:: Layout.add_attrib(tag, text, insert, dxfattribs=None)

   Add an :class:`Attrib` element, `tag` is the attrib-tag, `text` is the
   attrib content.

.. method:: Layout.add_polyline2D(points, dxfattribs=None)

   Add a :class:`Polyline` element, `points` is list of 2D points.

.. method:: Layout.add_polyline3D(points, dxfattribs=None)

   Add a :class:`Polyline` element, `points` is list of 3D points.

.. method:: Layout.add_polymesh(size=(3, 3), dxfattribs=None)

   Add a :class:`Polymesh` element, `size` is a 2-tuple (`mcount`, `ncount`).
   A polymesh is a grid of `mcount` x `ncount` vertices and every vertex has its
   own xyz-coordinates.

.. method:: Layout.add_polyface(dxfattribs=None)

   Add a :class:`Polyface` element.

Modelspace
==========

.. class:: Modelspace

   At this time the :class:`Modelspace` class is the :class:`Layout` class.

Paperspace
==========

.. class:: Paperspace

   At this time the :class:`Paperspace` class is the :class:`Layout` class.

BlockLayout
===========

.. class:: BlockLayout(Layout)

.. attribute:: BlockLayout.name

   The name of the associated block element. (read/write)

.. attribute:: BlockLayout.block

   Get the associated DXF *BLOCK* entity.

.. method:: BlockLayout.add_attdef(tag, insert, dxfattribs=None)

   Add an :class:`Attdef` element, `tag` is the attribute-tag, `insert` is the
   2D/3D insertion point of the Attribute.

.. method:: BlockLayout.attdefs()

   Iterator for included :class:`Attdef` entities.

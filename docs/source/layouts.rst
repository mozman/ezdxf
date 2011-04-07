Layout
======

A Layout represents and manages drawing entities, there are three different
layout objects:

- Modelspace is the common working space, containing basic drawing entities.
- Paperspaces are arrangements of objects for printing and plotting,
  this layouts can contain basic drawing entities, and viewports to the
  modelspace.

- BlockLayout works on an associated :class:`Block`, and Blocks are
  collections of drawing entities for reusing by block references.

.. class:: Layout

Access existing drawing entities
--------------------------------

.. method:: Layout.__iter__()

   Iterate over all drawing entities in this layout.

.. method:: Layout.__contains__(entity)

   Test if the layout contains the drawing element `entity`.

Create new drawing entities
---------------------------

.. method:: Layout.add_line(start, end, dxfattribs={})

   Add a :class:`Line` element, starting at 2D/3D point `start` and ending at
   the 2D/3D point `end`.

.. method:: Layout.add_circle(center, radius, dxfattribs={})

   Add a :class:`Circle` element, `center` is 2D/3D point, `radius` in drawing
   units.

.. method:: Layout.add_arc(center, radius, startangle, endangle, dxfattribs={})

   Add an :class:`Arc` element, `center` is 2D/3D point, `radius` in drawing
   units, `startangle` and `endangle` in degrees.

.. method:: Layout.add_solid(points, dxfattribs={})

   Add a :class:`Solid` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_trace(points, dxfattribs={})

   Add a :class:`Trace` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_3Dface(points, dxfattribs={})

   Add a :class:`3DFace` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_text(text, style='STANDARD', dxfattribs={})

   Add a :class:`Text` element, `text` is a string, `style` is a
   textstyle, see also :class:`Style`.

.. method:: Layout.add_blockref(name, insert, dxfattribs={})

   Add an :class:`Insert` element, `name` is the block name, `insert` is a
   2D/3D point.

.. method:: Layout.add_autoblockref(name, insert, values, dxfattribs={})

   Add an :class:`Insert` element, `name` is the block name, `insert` is a
   2D/3D point. Add :class:`Attdef`, defined in the block definition,
   automatically as :class:`Attrib` to the block reference, and set text of
   :class:`Attrib`. `values` is a dict with key=tag, value=text values.

.. method:: Layout.add_attrib(tag, text, insert, dxfattribs={})

   Add an :class:`Attrib` element, `tag` is the attrib-tag, `text` is the
   attrib content.

.. method:: Layout.add_polyline2D(points, dxfattribs={})

   Add a :class:`Polyline` element, `points` is list of 2D points.

.. method:: Layout.add_polyline3D(points, dxfattribs={})

   Add a :class:`Polyline` element, `points` is list of 3D points.

.. method:: Layout.add_polymesh(size=(3, 3), dxfattribs={})

   Add a :class:`Polymesh` element, `size` is a 2-tuple (`mcount`, `ncount`).
   A polymesh is a grid of `mcount` x `ncount` vertices and every vertex has its
   own xyz-coordinates.

.. method:: Layout.add_polyface(dxfattribs={})

   Add a :class:`Polyface` element.

Modelspace
==========

.. class:: Modelspace

   At this time the Modelspace class is the :class:`Layout` class.

Paperspace
==========

.. class:: Paperspace

   At this time the Paperspace class is the :class:`Layout` class.

BlockLayout
===========

.. class:: BlockLayout(Layout)

.. attribute:: BlockLayout.name

   The name of the associated block element.

.. method:: BlockLayout.add_attdef(tag, insert, dxfattribs={})

   Add an :class:`Attdef` element, `tag` is the attribute-tag, `insert` is the
   2D/3D insertion point of the Attribute.
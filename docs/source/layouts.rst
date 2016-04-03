.. _layout:

Layout
======

A Layout represents and manages drawing entities, there are three different
layout objects:

- Model space is the common working space, containing basic drawing entities.
- Paper spaces are arrangements of objects for printing and plotting,
  this layouts contains basic drawing entities and viewports to the model-space.
- BlockLayout works on an associated :class:`Block`, Blocks are
  collections of drawing entities for reusing by block references.

.. class:: Layout

Access existing entities
------------------------

.. method:: Layout.__iter__()

   Iterate over all drawing entities in this layout.

.. method:: Layout.__contains__(entity)

   Test if the layout contains the drawing element `entity`.

.. method:: Layout.query(query='*')

   Get included DXF entities matching the :ref:`entity query string` *query*.
   Returns a sequence of type :class:`EntityQuery`.

Create new entities
-------------------

.. method:: Layout.add_point(location, dxfattribs=None)

   Add a :class:`Point` element at `location`.

.. method:: Layout.add_line(start, end, dxfattribs=None)

   Add a :class:`Line` element, starting at 2D/3D point `start` and ending at
   the 2D/3D point `end`.

.. method:: Layout.add_circle(center, radius, dxfattribs=None)

   Add a :class:`Circle` element, `center` is 2D/3D point, `radius` in drawing
   units.

.. method:: Layout.add_ellipse(center, major_axis=(1, 0, 0), ratio=1, start_param=0, end_param=6.283185307, dxfattribs=None)

   Add an :class:`Ellipse` element, `center` is 2D/3D point, `major_axis` as vector, `ratio` is the ratio of minor axis
   to major axis, `start_param` and `end_param` defines start and end point of the ellipse, a full ellipse goes from 0
   to 2*pi. The ellipse goes from start to end param in *counter clockwise* direction.

.. method:: Layout.add_arc(center, radius, start_angle, end_angle, dxfattribs=None)

   Add an :class:`Arc` element, `center` is 2D/3D point, `radius` in drawing
   units, `start_angle` and `end_angle` in degrees. The arc goes from start_angle to end_angle in *counter clockwise*
   direction.

.. method:: Layout.add_solid(points, dxfattribs=None)

   Add a :class:`Solid` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_trace(points, dxfattribs=None)

   Add a :class:`Trace` element, `points` is list of 3 or 4 2D/3D points.

.. method:: Layout.add_3dface(points, dxfattribs=None)

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
   The :class:`Attrib` elements are placed relative to the insert point =
   block base point.

.. method:: Layout.add_attrib(tag, text, insert, dxfattribs=None)

   Add an :class:`Attrib` element, `tag` is the attrib-tag, `text` is the
   attrib content.

.. method:: Layout.add_polyline2d(points, dxfattribs=None)

   Add a :class:`Polyline` element, `points` is list of 2D points.

.. method:: Layout.add_polyline3d(points, dxfattribs=None)

   Add a :class:`Polyline` element, `points` is list of 3D points.

.. method:: Layout.add_polymesh(size=(3, 3), dxfattribs=None)

   Add a :class:`Polymesh` element, `size` is a 2-tuple (`mcount`, `ncount`).
   A polymesh is a grid of `mcount` x `ncount` vertices and every vertex has its
   own xyz-coordinates.

.. method:: Layout.add_polyface(dxfattribs=None)

   Add a :class:`Polyface` element.

.. method:: Layout.add_lwpolyline(points, dxfattribs=None)

   Add a 2D polyline, `points` is a list of 2D points. A :class:`LWPolyline` is defined as a single graphic entity and
   consume less disk space and memory. (requires DXF version AC1015 or newer)

.. method:: Layout.add_mtext(text, dxfattribs=None)

   Add a :class:`MText` element, which is a multiline text element with automatic text wrapping at boundaries.
   The `char_height` is the initial character height in drawing units, `width` is the width of the text boundary
   in drawing units. (requires DXF version AC1015 or newer)

.. method:: Layout.add_shape(name, insert=(0, 0, 0), size=1.0, dxfattribs=None)

   Add a :class:`Shape` reference to a external stored shape.

.. method:: Layout.add_ray(start, unit_vector, dxfattribs=None)

   Add a :class:`Ray` that starts at a point and continues to infinity (construction line).
   (requires DXF version AC1015 or newer)

.. method:: Layout.add_xline(start, unit_vector, dxfattribs=None)

   Add an infinity :class:`XLine` (construction line).
   (requires DXF version AC1015 or newer)

.. method:: Layout.add_spline(fit_points=None, dxfattribs=None)

   Add a :class:`Spline`, `fit_points` has to be a list (container or generator) of (x, y, z) tuples.
   (requires DXF version AC1015 or newer)

.. method:: Layout.add_body(acis_data="", dxfattribs=None)

   Add a :class:`Body` entity, `acis_data` has to be a list (container or generator) of text lines **without** line
   endings. (requires DXF version AC1015 or newer)

.. method:: Layout.add_region(acis_data="", dxfattribs=None)

   Add a :class:`Region` entity, `acis_data` has to be a list (container or generator) of text lines **without** line
   endings. (requires DXF version AC1015 or newer)

.. method:: Layout.add_3dsolid(acis_data="", dxfattribs=None)

   Add a :class:`3DSolid` entity, `acis_data` has to be a list (container or generator) of text lines **without** line
   endings. (requires DXF version AC1015 or newer)

.. method:: Layout.add_hatch(color=7, dxfattribs=None)

   Add a :class:`Hatch` entity, *color* as ACI (AutoCAD Color Index), default is 7 (black/white).
   (requires DXF version AC1015 or newer)

.. method:: Layout.add_image(image_def, insert, size_in_units, rotation=0, dxfattribs=None)

   Add an :class:`Image` entity, *insert* is the insertion point as (x, y [,z]) tuple, *size_in_units* is the image
   size as (x, y) tuple in drawing units, *image_def* is the required :class:`ImageDef`, *rotation* is the rotation
   angle around the z-axis in degrees. Create :class:`ImageDef` by the :class:`Drawing` factory function
   :meth:`~Drawing.add_image_def`, see :ref:`tut_image`. (requires DXF version AC1015 or newer)

.. method:: Layout.add_underlay(underlay_def, insert=(0, 0, 0), scale=(1, 1, 1), rotation=0, dxfattribs=None)

   Add an :class:`Underlay` entity, *insert* is the insertion point as (x, y [,z]) tuple, *scale* is the underlay
   scaling factor as (x, y, z) tuple, *underlay_def* is the required :class:`UnderlayDefinition`, *rotation* is the
   rotation angle around the z-axis in degrees. Create :class:`UnderlayDef` by the :class:`Drawing` factory function
   :meth:`~Drawing.add_underlay_def`, see :ref:`tut_underlay`. (requires DXF version AC1015 or newer)

Delete entities
---------------

.. method:: Layout.delete_entity(entity)

   Delete `entity` from layout and drawing database.

.. method:: Layout.delete_all_entities()

   Delete all `entities` from layout and drawing database.

.. _model space:

Model Space
===========

.. class:: Modelspace

   At this time the :class:`Modelspace` class is the :class:`Layout` class.

.. _paper space:

Paper Space
===========

.. class:: Paperspace

   At this time the :class:`Paperspace` class is the :class:`Layout` class.

.. _block layout:

BlockLayout
===========

.. class:: BlockLayout(Layout)

.. attribute:: BlockLayout.name

   The name of the associated block element. (read/write)

.. attribute:: BlockLayout.block

   Get the associated DXF *BLOCK* entity.

.. method:: BlockLayout.add_attdef(tag, insert=(0, 0), dxfattribs=None)

   Add an :class:`Attdef` element, `tag` is the attribute-tag, `insert` is the
   2D/3D insertion point of the Attribute. Set position and alignment by the idiom::

      myblock.add_attdef('NAME').set_pos((2, 3), align='MIDDLE_CENTER')

.. method:: BlockLayout.attdefs()

   Iterator for included :class:`Attdef` entities.

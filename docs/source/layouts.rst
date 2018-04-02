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

Paper Space Layout Setup
------------------------

.. method:: Layout.page_setup(size=(297, 210), margins=(10, 15, 10, 15), units='mm', offset=(0, 0), rotation=0, scale=16, name='ezdxf', device='DWG to PDF.pc3')

    Setup plot settings and paper size and reset viewports. All parameters in given *units* (mm or inch).
    DXF R12 not supported yet.

    :param size: paper size as (width, height) tuple
    :param margins: (top, right, bottom, left) hint: clockwise
    :param units: 'mm' or 'inch'
    :param offset: plot origin offset as (x, y) tuple
    :param rotation: 0=no rotation, 1=90deg count-clockwise, 2=upside-down, 3=90deg clockwise
    :param scale: int 0-32 = standard scale type or tuple(numerator, denominator) e.g. (1, 50) for 1:50
    :param name: paper name prefix '{name}_({width}_x_{height}_{unit})'
    :param device: device .pc3 configuration file or system printer name

.. method:: Layout.reset_viewports()

    Delete all existing viewports, and add a new main viewport. (in :meth:`~Layout.page_setup` included)

.. method:: Layout.reset_extends()

    Reset paper space extends. (in :meth:`~Layout.page_setup` included)

.. method:: Layout.reset_paper_limits()

    Reset paper space limits. (in :meth:`~Layout.page_setup` included)

.. method:: Layout.get_paper_limits()

    Returns paper limits in plot paper units, relative to the plot origin, as tuple ((x1, y1), (x2, y2)).
    Lower left corner is (x1, y1), upper right corner is (x2, y2).

    The plot origin is lower left corner of printable area + plot origin offset.

.. method:: Layout.set_plot_type(value=5)

    Set plot type:

    - 0 = last screen display
    - 1 = drawing extents
    - 2 = drawing limits
    - 3 = view specific (defined by Layout.dxf.plot_view_name)
    - 4 = window specific (defined by Layout.set_plot_window_limits())
    - 5 = layout information (default)

.. method:: Layout.set_plot_style(name='ezdxf.ctb', show=False)

    Set current plot style e.g. "acad.ctb", and *show* impact of plot style also on screen.

.. method:: Layout.set_plot_window(lower_left=(0, 0), upper_right=(0, 0))

    Set plot window size in (scaled) paper space units, and relative to the plot origin.

Access existing entities
========================

.. method:: Layout.__iter__()

   Iterate over all drawing entities in this layout.

.. method:: Layout.__contains__(entity)

   Test if the layout contains the drawing element `entity` (aka `in` operator).

.. method:: Layout.query(query='*')

   Get included DXF entities matching the :ref:`entity query string` *query*.
   Returns a sequence of type :class:`EntityQuery`.

.. method:: Layout.groupby(dxfattrib='', key=None)

   Returns a dict of entity lists, where entities are grouped by a dxfattrib or a key function.

   :param str dxfattrib: grouping DXF attribute like 'layer'
   :param function key: key function, which accepts a DXFEntity as argument, returns grouping key of this entity or
       None for ignore this object. Reason for ignoring: a queried DXF attribute is not supported by this entity

.. _Entity Factory Functions:

Create new entities
===================

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

   Add a 2D polyline, `points` is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples. Set start_width,
   end_width to 0 to be ignored (x, y, 0, 0, bulge). A :class:`LWPolyline` is defined as a single graphic entity and
   consume less disk space and memory. (requires DXF version AC1015 or later)

.. method:: Layout.add_mtext(text, dxfattribs=None)

   Add a :class:`MText` element, which is a multiline text element with automatic text wrapping at boundaries.
   The `char_height` is the initial character height in drawing units, `width` is the width of the text boundary
   in drawing units. (requires DXF version AC1015 or later)

.. method:: Layout.add_shape(name, insert=(0, 0, 0), size=1.0, dxfattribs=None)

   Add a :class:`Shape` reference to a external stored shape.

.. method:: Layout.add_ray(start, unit_vector, dxfattribs=None)

   Add a :class:`Ray` that starts at a point and continues to infinity (construction line).
   (requires DXF version AC1015 or later)

.. method:: Layout.add_xline(start, unit_vector, dxfattribs=None)

   Add an infinity :class:`XLine` (construction line).
   (requires DXF version AC1015 or later)

.. method:: Layout.add_spline(fit_points=None, dxfattribs=None)

   Add a :class:`Spline`, `fit_points` has to be a list (container or generator) of (x, y, z) tuples.
   (requires DXF version AC1015 or later)

   AutoCAD creates a spline through fit points by a proprietary algorithm. `ezdxf` can not reproduce the control point
   calculation.

.. method:: Layout.add_open_spline(control_points, degree=3, dxfattribs=None)

   Add an open uniform :class:`Spline`, `control_points` has to be a list (container or generator) of (x, y, z) tuples,
   `degree` specifies degree of spline. (requires DXF version AC1015 or later)

   Open uniform B-splines start and end at your first and last control points.

.. method:: Layout.add_closed_spline(control_points, degree=3, dxfattribs=None)

   Add a closed uniform :class:`Spline`, `control_points` has to be a list (container or generator) of (x, y, z) tuples,
   `degree` specifies degree of spline. (requires DXF version AC1015 or later)

   Closed uniform B-splines is a closed curve start and end at the first control points.

.. method:: Layout.add_rational_spline(control_points, weights, degree=3, dxfattribs=None)

   Add an open rational uniform :class:`Spline`, `control_points` has to be a list (container or generator) of (x, y, z)
   tuples, `weights` has to be a list of values, which defines the influence of the associated control point, therefor
   count of control points has to be equal to the count of weights, `degree` specifies degree of spline. (requires DXF
   version AC1015 or later)

   Open rational uniform B-splines start and end at your first and last control points, and have additional control
   possibilities by weighting each control point.

.. method:: Layout.add_closed_rational_spline(control_points, weights, degree=3, dxfattribs=None)

   Add a closed rational uniform :class:`Spline`, `control_points` has to be a list (container or generator) of (x, y, z)
   tuples, `weights` has to be a list of values, which defines the influence of the associated control point, therefor
   count of control points has to be equal to the count of weights, `degree` specifies degree of spline. (requires DXF
   version AC1015 or later)

   Closed rational uniform B-splines start and end at the first control point, and have additional control
   possibilities by weighting each control point.

.. method:: Layout.add_spline_control_frame(fit_points, degree=3, method='distance', power=.5, dxfattribs=None)

    Create and add B-spline control frame from fit points.

    Supported methods are:

    - uniform: creates a uniform t vector, [0 \.. 1] equally spaced
    - distance: creates a t vector with values proportional to the fit point distances
    - centripetal: creates a t vector with values proportional to the fit point distances^power

    None of this methods matches the spline created from fit points by AutoCAD.

    :param fit_points: fit points of B-spline
    :param degree: degree of B-spline
    :param method: calculation method for parameter vector t
    :param power: power for centripetal method
    :param dxfattribs: DXF attributes for SPLINE entity
    :returns: DXF :class:`Spline` object

.. method:: Layout.add_spline_approx(fit_points, count, degree=3, method='distance', power=.5, dxfattribs=None)

    Approximate B-spline by a reduced count of control points, given are the fit points and the degree of the B-spline.

    - uniform: creates a uniform t vector, [0 \.. 1] equally spaced
    - distance: creates a t vector with values proportional to the fit point distances
    - centripetal: creates a t vector with values proportional to the fit point distances^power

    :param fit_points: all fit points of B-spline
    :param count: count of designated control points
    :param degree: degree of B-spline
    :param method: calculation method for parameter vector t
    :param power: power for centripetal method
    :param dxfattribs: DXF attributes for SPLINE entity
    :returns: DXF :class:`Spline` object

.. method:: Layout.add_body(acis_data="", dxfattribs=None)

   Add a :class:`Body` entity, `acis_data` has to be a list (container or generator) of text lines **without** line
   endings. (requires DXF version AC1015 or later)

.. method:: Layout.add_region(acis_data="", dxfattribs=None)

   Add a :class:`Region` entity, `acis_data` has to be a list (container or generator) of text lines **without** line
   endings. (requires DXF version AC1015 or later)

.. method:: Layout.add_3dsolid(acis_data="", dxfattribs=None)

   Add a :class:`3DSolid` entity, `acis_data` has to be a list (container or generator) of text lines **without** line
   endings. (requires DXF version AC1015 or later)

.. method:: Layout.add_hatch(color=7, dxfattribs=None)

   Add a :class:`Hatch` entity, *color* as ACI (AutoCAD Color Index), default is 7 (black/white).
   (requires DXF version AC1015 or later)

.. method:: Layout.add_image(image_def, insert, size_in_units, rotation=0, dxfattribs=None)

   Add an :class:`Image` entity, *insert* is the insertion point as (x, y [,z]) tuple, *size_in_units* is the image
   size as (x, y) tuple in drawing units, *image_def* is the required :class:`ImageDef`, *rotation* is the rotation
   angle around the z-axis in degrees. Create :class:`ImageDef` by the :class:`Drawing` factory function
   :meth:`~Drawing.add_image_def`, see :ref:`tut_image`. (requires DXF version AC1015 or later)

.. method:: Layout.add_underlay(underlay_def, insert=(0, 0, 0), scale=(1, 1, 1), rotation=0, dxfattribs=None)

   Add an :class:`Underlay` entity, *insert* is the insertion point as (x, y [,z]) tuple, *scale* is the underlay
   scaling factor as (x, y, z) tuple, *underlay_def* is the required :class:`UnderlayDefinition`, *rotation* is the
   rotation angle around the z-axis in degrees. Create :class:`UnderlayDef` by the :class:`Drawing` factory function
   :meth:`~Drawing.add_underlay_def`, see :ref:`tut_underlay`. (requires DXF version AC1015 or later)

.. method:: Layout.add_entity(dxfentity)

   Add an existing DXF entity to a layout, but be sure to unlink (:meth:`~Layout.unlink_entity()`) first the entity from
   the previous owner layout.


Delete entities
===============

.. method:: Layout.unlink_entity(entity)

   Unlink `entity` from layout but does not delete entity from the drawing database.

.. method:: Layout.delete_entity(entity)

   Delete `entity` from layout and drawing database.

.. method:: Layout.delete_all_entities()

   Delete all `entities` from layout and drawing database.

.. _model space:

Model Space
===========

.. class:: Modelspace

   At this time the :class:`Modelspace` class is the :class:`Layout` class.


.. method:: Modelspace.new_geodata(dxfattribs=None)

    Creates a new :class:`GeoData` entity and replaces existing ones. The GEODATA entity resides in the OBJECTS section
    and NOT in the layout entity space and it is linked to the layout by an extension dictionary located in BLOCK_RECORD
    of the layout.

    The GEODATA entity requires DXF version R2010 (AC1024) or later. The DXF Reference does not document if other
    layouts than model space supports geo referencing, so getting/setting geo data may only make sense for the model
    space layout, but it is also available in paper space layouts.

.. method:: Modelspace.get_geodata(dxfattribs=None)

    Returns the :class:`GeoData` entity associated to this layout or None.


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

.. method:: BlockLayout.has_attdef(tag)

   Returns `True` if an attdef `tag` exists else `False`.

.. method:: BlockLayout.get_attdef(tag)

   Get the attribute definition object :class:`Attdef` with :code:`object.dxf.tag == tag`, returns
   :code:`None` if not found.

.. method:: BlockLayout.get_attdef_text(tag, default=None)

   Get content text for attdef `tag` as string or return `default` if no attdef `tag` exists.


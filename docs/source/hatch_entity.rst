Hatch
=====

.. class:: Hatch

Introduced in DXF version R13 (AC1012), *dxftype* is HATCH.

Fills an enclosed area defined by one or more boundary paths with a hatch pattern, solid fill, or gradient fill.
Create :class:`Hatch` in layouts and blocks by factory function :meth:`~Layout.add_hatch`.

DXF Attributes for Hatch
------------------------

.. attribute:: Hatch.dxf.pattern_name

pattern name as string

.. attribute:: Hatch.dxf.solid_fill

solid fill = 1, pattern fill = 0 (better use: :meth:`Hatch.set_solid_fill`, :meth:`Hatch.set_pattern_fill`)

.. attribute:: Hatch.dxf.associative

1 for associative hatch else 0, associations not handled by ezdxf, you have to set the handles to the associated DXF
entities by yourself.

.. attribute:: Hatch.dxf.hatch_style

0 = normal; 1 = outer; 2 = ignore (search for AutoCAD help for more information)

.. attribute:: Hatch.dxf.pattern_type

0 = user; 1 = predefined; 2 = custom; (???)

.. attribute:: Hatch.dxf.pattern_angle

Pattern angle in degrees (360 deg = circle)

.. attribute:: Hatch.dxf.pattern_scale

.. attribute:: Hatch.dxf.pattern_double

1 = double else 0

.. attribute:: Hatch.dxf.n_seed_points

Count of seed points (better user: :meth:`Hatch.get_seed_points`)


Hatch Attributes
----------------

.. attribute:: Hatch.has_solid_fill

*True* if hatch has a solid fill else *False*. (read only)

.. attribute:: Hatch.has_pattern_fill

*True* if hatch has a pattern fill else *False*. (read only)

.. attribute:: Hatch.has_gradient_fill

*True* if hatch has a gradient fill else *False*. A hatch with gradient fill has also a solid fill. (read only)

.. attribute:: Hatch.bgcolor

Property background color as (r, g, b) tuple, rgb values in range 0..255 (read/write/del)

usage::

    color = hatch.bgcolor  # get background color as (r, g, b) tuple
    hatch.bgcolor = (10, 20, 30)  # set background color
    del hatch.bgcolor  # delete background color

.. method:: Hatch.edit_boundary()

Context manager to edit hatch boundary data, yields a :class:`BoundaryPathData` object.

.. method:: Hatch.edit_pattern()

Context manager to edit hatch pattern data, yields a :class:`PatternData` object.

.. method:: Hatch.set_pattern_definition(lines)

Setup hatch patten definition by a list of definition lines and a definition line is a 4-tuple [angle, base_point,
offset, dash_length_items]

- *angle*: line angle in degrees
- *base-point*: (x, y) tuple
- *offset*: (dx, dy) tuple, added to base point for next line and so on
- *dash_length_items*: list of dash items (item > 0 is a line, item < 0 is a gap and item == 0.0 is a point)

:param list lines: list of definition lines

.. method:: Hatch.set_solid_fill(color=7, style=1, rgb=None)

Set :class:`Hatch` to solid fill mode and removes all gradient and pattern fill related data.

:param int color: ACI (AutoCAD Color Index) in range 0 to 256, (0 = BYBLOCK; 256 = BYLAYER)
:param int style: hatch style (0 = normal; 1 = outer; 2 = ignore)
:param tuple rgb: true color value as (r, g, b) tuple - has higher priority than *color*. True color support requires at least DXF version AC1015.

.. method:: Hatch.set_gradient(color1=(0, 0, 0), color2=(255, 255, 255), rotation=0., centered=0., one_color=0, tint=0., name='LINEAR')

Set :class:`Hatch` to gradient fill mode and removes all pattern fill related data. Gradient support requires at
least DXF version AC1018. A gradient filled hatch is also a solid filled hatch.

:param tuple color1: (r, g, b) tuple for first color, rgb values as int in range 0..255
:param tuple color2: (r, g, b) tuple for second color, rgb values as int in range 0..255
:param float rotation: rotation in degrees (360 deg = circle)
:param int centered: determines whether the gradient is centered or not
:param int one_color: 1 for gradient from *color1* to tinted *color1*
:param float tint: determines the tinted target *color1* for a one color gradient. (valid range 0.0 to 1.0)
:param str name: name of gradient type, default 'LINEAR'

Valid gradient type names are:

- LINEAR
- CYLINDER
- INVCYLINDER
- SPHERICAL
- INVSPHERICAL
- HEMISPHERICAL
- INVHEMISPHERICAL
- CURVED
- INVCURVED

.. method:: Hatch.get_gradient()

Get gradient data, returns a :class:`GradientData` object.

.. method:: Hatch.edit_gradient()

Context manager to edit hatch gradient data, yields a :class:`GradientData` object.

.. method:: Hatch.set_pattern_fill(name, color=7, angle=0., scale=1., double=0, style=1, pattern_type=1, definition=None)

Set :class:`Hatch` to pattern fill mode. Removes all gradient related data.

:param int color: AutoCAD Color Index in range 0 to 256, (0 = BYBLOCK; 256 = BYLAYER)
:param float angle: angle of pattern fill in degrees (360 deg = circle)
:param float scale: pattern scaling
:param int double: double flag
:param int style: hatch style (0 = normal; 1 = outer; 2 = ignore)
:param int pattern_type: pattern type (0 = user-defined; 1 = predefined; 2 = custom) ???
:param list definition: list of definition lines and a definition line is a 4-tuple [angle, base_point,
    offset, dash_length_items], see :meth:`Hatch.set_pattern_definition`

.. method:: Hatch.get_seed_points()

Get seed points as list of (x, y) points, I don't know why there can be more than one seed point.

.. method:: Hatch.set_seed_points(points)

Set seed points, *points* is a list of (x, y) tuples, I don't know why there can be more than one seed point.


.. seealso::

    :ref:`tut_hatch`



Hatch Boundary Helper Classes
-----------------------------

.. class:: BoundaryPathData

Defines the borders of the hatch, a hatch can consist of more than one path.

.. attribute:: BoundaryPathData.paths

List of all boundary paths. Contains :class:`PolylinePath` and :class:`EdgePath` objects. (read/write)

.. method:: BoundaryPathData.add_polyline_path(path_vertices, is_closed=1, flags=1)

Create and add a new :class:`PolylinePath` object.

:param list path_vertices: list of polyline vertices as (x, y) or (x, y, bulge) tuples.
:param int is_closed: 1 for a closed polyline else 0
:param int flags: external(1) or outermost(16) or default (0)

.. method:: BoundaryPathData.add_edge_path(flags=1)

Create and add a new :class:`EdgePath` object.

:param int flags: external(1) or outermost(16) or default (0)

.. method:: BoundaryPathData.clear()

Remove all boundary paths.



.. class:: PolylinePath

A polyline as hatch boundary path.

.. attribute:: PolylinePath.path_type_flags

external(1) or outermost(16) or default (0) - polyline(2) will be set by *ezdxf*

My interpretation of the :attr:`path_type_flags`, see also :ref:`tut_hatch`:

* external - path is part of the hatch outer border
* outermost - path is completely inside of one or more external paths
* default - path is completely inside of one or more outermost paths

If there are troubles with AutoCAD, maybe the hatch entity contains the pixel size tag (47) - delete it
:code:`hatch.AcDbHatch.remove_tags([47])` and maybe the problem is solved. *ezdxf* does not use the pixel size tag,
but it can occur in DXF files created by other applications.

.. attribute:: PolylinePath.is_closed

*True* if polyline path is closed else *False*.

.. attribute:: PolylinePath.vertices

List of path vertices as (x, y, bulge) tuples. (read/write)

.. attribute:: PolylinePath.source_boundary_objects

List of handles of the associated DXF entities for associative hatches. There is no support for associative hatches
by ezdxf you have to do it all by yourself. (read/write)

.. method:: PolylinePath.set_vertices(vertices, is_closed=1)

Set new vertices for the polyline path, a vertex has to be a (x, y) or a (x, y, bulge) tuple.

.. method:: PolylinePath.clear()

Removes all vertices and all links to associated DXF objects (:attr:`PolylinePath.source_boundary_objects`).



.. class:: EdgePath

Boundary path build by edges. There are four different edge types: :class:`LineEdge`, :class:`ArcEdge`,
:class:`EllipseEdge` of :class:`SplineEdge`. Make sure there are no gaps between edges. AutoCAD in this regard is
very picky. *ezdxf* performs no checks on gaps between the edges.

.. attribute:: EdgePath.path_type_flags

external(1) or outermost(16) or default (0), see :attr:`PolylinePath.path_type_flags`

.. attribute:: EdgePath.edges

List of boundary edges of type :class:`LineEdge`, :class:`ArcEdge`, :class:`EllipseEdge` of :class:`SplineEdge`

.. attribute:: EdgePath.source_boundary_objects

Required for associative hatches, list of handles to the associated DXF entities.

.. method:: EdgePath.clear()

Delete all edges.

.. method:: EdgePath.add_line(start, end)

Add a :class:`LineEdge` from *start* to *end*.

:param tuple start: start point of line, (x, y) tuple
:param tuple end: end point of line, (x, y) tuple

.. method:: EdgePath.add_arc(center, radius=1., start_angle=0., end_angle=360., is_counter_clockwise=0)

Add an :class:`ArcEdge`.

:param tuple center: center point of arc, (x, y) tuple
:param float radius: radius of circle
:param float start_angle: start angle of arc in degrees
:param float end_angle: end angle of arc in degrees
:param int is_counter_clockwise: 1 for yes 0 for no

.. method:: EdgePath.add_ellipse(center, major_axis_vector=(1., 0.), minor_axis_length=1., start_angle=0., end_angle=360., is_counter_clockwise=0)

Add an :class:`EllipseEdge`.

:param tuple center: center point of ellipse, (x, y) tuple
:param tuple major_axis: vector of major axis as (x, y) tuple
:param float ratio: ratio of minor axis to major axis as float
:param float start_angle: start angle of ellipse in degrees
:param float end_angle: end angle of ellipse in degrees
:param int is_counter_clockwise: 1 for yes 0 for no

.. method:: EdgePath.add_spline(fit_points=None, control_points=None, knot_values=None, weights=None, degree=3, rational=0, periodic=0)

Add a :class:`SplineEdge`.

:param list fit_points: points through which the spline must go, at least 3 fit points are required. list of (x, y) tuples
:param list control_points: affects the shape of the spline, mandatory amd AutoCAD crashes on invalid data. list of (x, y) tuples
:param list knot_values: (knot vector) mandatory and AutoCAD crashes on invalid data. list of floats; *ezdxf* provides two
    tool functions to calculate valid knot values: :code:`ezdxf.tools.knot_values(n_control_points, degree)` and
    :code:`ezdxf.tools.knot_values_uniform(n_control_points, degree)`
:param list weights: weight of control point, not mandatory, list of floats.
:param int degree: degree of spline
:param int rational: 1 for rational spline, 0 for none rational spline
:param int periodic: 1 for periodic spline, 0 for none periodic spline

.. warning::

    Unlike for the spline entity AutoCAD does not calculate the necessary *knot_values* for the spline edge itself.
    On the contrary, if the *knot_values* in the spline edge are missing or invalid  AutoCAD **crashes**.

.. class:: LineEdge

Straight boundary edge.

.. attribute:: LineEdge.start

Start point as (x, y) tuple. (read/write)

.. attribute:: LineEdge.end

End point as (x, y) tuple. (read/write)

.. class:: ArcEdge

Arc as boundary edge.

.. attribute:: ArcEdge.center

Center point of arc as (x, y) tuple. (read/write)

.. attribute:: ArcEdge.radius

Arc radius as float. (read/write)

.. attribute:: ArcEdge.start_angle

Arc start angle in degrees (360 deg = circle). (read/write)

.. attribute:: ArcEdge.end_angle

Arc end angle in degrees (360 deg = circle). (read/write)

.. attribute:: ArcEdge.is_counter_clockwise

1 for counter clockwise arc else 0. (read/write)

.. class:: EllipseEdge

Elliptic arc as boundary edge.

.. attribute:: EllipseEdge.major_axis_vector

Ellipse major axis vector as (x, y) tuple. (read/write)

.. attribute:: EllipseEdge.minor_axis_length

Ellipse minor axis length as float. (read/write)

.. attribute:: EllipseEdge.radius

Ellipse radius as float. (read/write)

.. attribute:: EllipseEdge.start_angle

Ellipse start angle in degrees (360 deg = circle). (read/write)

.. attribute:: EllipseEdge.end_angle

Ellipse end angle in degrees (360 deg = circle). (read/write)

.. attribute:: EllipseEdge.is_counter_clockwise

1 for counter clockwise ellipse else 0. (read/write)

.. class:: SplineEdge

Spline as boundary edge.

.. attribute:: SplineEdge.degree

Spline degree as int. (read/write)

.. attribute:: SplineEdge.rational

1 for rational spline else 0. (read/write)

.. attribute:: SplineEdge.periodic

1 for periodic spline else 0. (read/write)

.. attribute:: SplineEdge.knot_values

List of knot values as floats. (read/write)

.. attribute:: SplineEdge.control_points

List of control points as (x, y) tuples. (read/write)

.. attribute:: SplineEdge.fit_points

List of fit points as (x, y) tuples. (read/write)

.. attribute:: SplineEdge.weights

List of weights (of control points) as floats. (read/write)

.. attribute:: SplineEdge.start_tangent

Spline start tangent (vector)  as (x, y) tuple. (read/write)

.. attribute:: SplineEdge.end_tangent

Spline end tangent (vector)  as (x, y) tuple. (read/write)

Hatch Pattern Definition Helper Classes
---------------------------------------

.. class:: PatternData

.. attribute:: PatternData.lines

List of pattern definition lines (read/write). see :class:`PatternDefinitionLine`

.. method:: PatternData.new_line(angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None)

Create a new pattern definition line, but does not add the line to the :attr:`PatternData.lines` attribute.

.. method:: PatternData.add_line(angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None)

Create a new pattern definition line and add the line to the :attr:`PatternData.lines` attribute.

.. method:: PatternData.clear()

Delete all pattern definition lines.

.. class:: PatternDefinitionLine

Represents a pattern definition line, use factory function :meth:`PatternData.new_line` to create new pattern
definition lines.

.. attribute:: PatternDefinitionLine.angle

Line angle in degrees (circle = 360 deg). (read/write)

.. attribute:: PatternDefinitionLine.base_point

Base point as (x, y) tuple. (read/write)

.. attribute:: PatternDefinitionLine..offset

Offset as (x, y) tuple. (read/write)

.. attribute:: PatternDefinitionLine.dash_length_items

List of dash length items (item > 0 is line, < 0 is gap, 0.0 = dot). (read/write)

Hatch Gradient Fill Helper Classes
----------------------------------

.. class:: GradientData

.. attribute:: GradientData.color1

First rgb color as (r, g, b) tuple, rgb values in range 0 to 255. (read/write)

.. attribute:: GradientData.color2

Second rgb color as (r, g, b) tuple, rgb values in range 0 to 255. (read/write)

.. attribute:: GradientData.one_color

If :attr:`~GradientData.one_color` is 1 - the hatch is filled with a smooth transition between
:attr:`~GradientData.color1` and a specified :attr:`~GradientData.tint` of :attr:`~GradientData.color1`. (read/write)

.. attribute:: GradientData.rotation

Gradient rotation in degrees (circle = 360 deg). (read/write)

.. attribute:: GradientData.centered

Specifies a symmetrical gradient configuration. If this option is not selected, the gradient fill is shifted up and
to the left, creating the illusion of a light source to the left of the object. (read/write)

.. attribute:: GradientData.tint

Specifies the tint (color1 mixed with white) of a color to be used for a gradient fill of one color. (read/write)

.. seealso::

    :ref:`tut_hatch_pattern`

Hatch
=====

.. module:: ezdxf.entities
    :noindex:

The HATCH entity (`DXF Reference`_) fills a closed area defined by one or
more boundary paths by a hatch pattern, a solid fill, or a gradient fill.

All points in :ref:`OCS` as (x, y) tuples (:attr:`Hatch.dxf.elevation` is the
z-axis value).

There are two different hatch pattern default scaling, depending on the HEADER
variable $MEASUREMENT, one for ISO measurement (m, cm, mm, ...) and one for
imperial measurement (in, ft, yd, ...).

The default scaling for predefined hatch pattern will be chosen according this
measurement setting in the HEADER section, this replicates the behavior of
BricsCAD and other CAD applications. `Ezdxf` uses the ISO pattern definitions as
a base line and scales this pattern down by factor 1/25.6 for imperial
measurement usage.
The pattern scaling is independent from the drawing units of the document
defined by the HEADER variable $INSUNITS.

.. seealso::

    :ref:`tut_hatch` and :ref:`DXF Units`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'HATCH'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_hatch`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-C6C71CED-CE0F-4184-82A5-07AD6241F15B

.. rubric:: Boundary paths classes

Path manager: :class:`BoundaryPaths`

- :class:`PolylinePath`
- :class:`EdgePath`
    - :class:`LineEdge`
    - :class:`ArcEdge`
    - :class:`EllipseEdge`
    - :class:`SplineEdge`

.. rubric:: Pattern and gradient classes

- :class:`Pattern`
- :class:`PatternLine`
- :class:`Gradien`

.. class:: Hatch

    .. attribute:: dxf.pattern_name

        Pattern name as string

    .. attribute:: dxf.solid_fill

        === ==========================================================
        1   solid fill,  use method :meth:`Hatch.set_solid_fill`
        0   pattern fill, use method :meth:`Hatch.set_pattern_fill`
        === ==========================================================

    .. attribute:: dxf.associative

        === =========================
        1   associative hatch
        0   not associative hatch
        === =========================

        Associations are not managed by `ezdxf`.

    .. attribute:: dxf.hatch_style

        === ========
        0   normal
        1   outer
        2   ignore
        === ========

        (search AutoCAD help for more information)

    .. attribute:: dxf.pattern_type

        === ===================
        0   user
        1   predefined
        2   custom
        === ===================

    .. attribute:: dxf.pattern_angle

        The actual pattern rotation angle in degrees (float). Changing this value does not
        rotate the pattern, use :meth:`~Hatch.set_pattern_angle` for this task.

    .. attribute:: dxf.pattern_scale

        The actual pattern scale factor (float). Changing this value does not
        scale the pattern use :meth:`~Hatch.set_pattern_scale` for this task.

    .. attribute:: dxf.pattern_double

        1 = double pattern size else 0. (int)

    .. attribute:: dxf.n_seed_points

        Count of seed points (use :meth:`get_seed_points`)

    .. attribute:: dxf.elevation

       Z value represents the elevation height of the :ref:`OCS`. (float)

    .. attribute:: paths

        :class:`BoundaryPaths` object.

    .. attribute:: pattern

        :class:`Pattern` object.

    .. attribute:: gradient

        :class:`Gradient` object.

    .. attribute:: seeds

        A list of seed points as (x, y) tuples.

    .. autoproperty:: has_solid_fill

    .. autoproperty:: has_pattern_fill

    .. autoproperty:: has_gradient_data

    .. autoproperty:: bgcolor

    .. automethod:: set_pattern_definition

    .. automethod:: set_pattern_scale

    .. automethod:: set_pattern_angle

    .. automethod:: set_solid_fill

    .. automethod:: set_pattern_fill

    .. automethod:: set_gradient

    .. automethod:: set_seed_points

    .. automethod:: transform(m: Matrix44) -> Hatch

    .. automethod:: associate

    .. automethod:: remove_association

Boundary Paths
--------------

The hatch entity is build by different path types, these are the
filter flags for the :attr:`Hatch.dxf.hatch_style`:

- EXTERNAL: defines the outer boundary of the hatch
- OUTERMOST: defines the first tier of inner hatch boundaries
- DEFAULT: default boundary path

As you will learn in the next sections, these are more the recommended
usage type for the flags, but the fill algorithm doesn't care much about that,
for instance an OUTERMOST path doesn't have to be inside the EXTERNAL path.

Island Detection
----------------

In general the island detection algorithm works always from outside to inside
and alternates filled and unfilled areas. The area between then 1st and the 2nd
boundary is filled, the area between the 2nd and the 3rd boundary is unfilled
and so on. The different hatch styles defined by the :attr:`Hatch.dxf.hatch_style`
attribute are created by filtering some boundary path types.

Hatch Style
-----------

- HATCH_STYLE_IGNORE: Ignores all paths except the paths marked as EXTERNAL, if
  there are more than one path marked as EXTERNAL, they are filled in NESTED
  style. Creates no hatch if no path is marked as EXTERNAL.
- HATCH_STYLE_OUTERMOST: Ignores all paths marked as DEFAULT, remaining EXTERNAL
  and OUTERMOST paths are filled in NESTED style. Creates no hatch if no path is
  marked as EXTERNAL or OUTERMOST.
- HATCH_STYLE_NESTED: Use all existing paths.

Hatch Boundary Classes
----------------------

.. class:: BoundaryPaths

    Defines the borders of the hatch, a hatch can consist of more than one path.

    .. attribute:: paths

        List of all boundary paths. Contains :class:`PolylinePath` and
        :class:`EdgePath` objects. (read/write)

    .. automethod:: external_paths

    .. automethod:: outermost_paths

    .. automethod:: default_paths

    .. automethod:: rendering_paths

    .. automethod:: add_polyline_path

    .. automethod:: add_edge_path

    .. automethod:: polyline_to_edge_paths

    .. automethod:: edge_to_polyline_paths

    .. automethod:: arc_edges_to_ellipse_edges

    .. automethod:: ellipse_edges_to_spline_edges

    .. automethod:: spline_edges_to_line_edges

    .. automethod:: all_to_spline_edges

    .. automethod:: all_to_line_edges

    .. automethod:: clear


.. class:: BoundaryPathType

    .. attribute:: POLYLINE

        polyline path type

    .. attribute:: EDGE

        edge path type


.. class:: PolylinePath

    A polyline as hatch boundary path.

    .. attribute:: type

        Path type as :attr:`BoundaryPathType.POLYLINE` enum

    .. attribute:: path_type_flags

        (bit coded flags)

        === ====================================
        0   default
        1   external
        2   polyline, will be set by `ezdxf`
        16  outermost
        === ====================================

        My interpretation of the :attr:`path_type_flags`, see also :ref:`tut_hatch`:

            - external: path is part of the hatch outer border
            - outermost: path is completely inside of one or more external paths
            - default: path is completely inside of one or more outermost paths

        If there are troubles with AutoCAD, maybe the hatch entity has the
        :attr:`Hatch.dxf.pixel_size` attribute set - delete it
        :code:`del hatch.dxf.pixel_size` and maybe the problem is solved.
        `Ezdxf` does not use the :attr:`Hatch.dxf.pixel_size` attribute, but it
        can occur in DXF files created by other applications.

    .. attribute:: PolylinePath.is_closed

        ``True`` if polyline path is closed.

    .. attribute:: vertices

        List of path vertices as (x, y, bulge)-tuples. (read/write)

    .. attribute:: source_boundary_objects

        List of handles of the associated DXF entities for associative hatches.
        There is no support for associative hatches by `ezdxf`, you have to do
        it all by yourself. (read/write)

    .. automethod:: set_vertices

    .. automethod:: clear


.. class:: EdgePath

    Boundary path build by edges. There are four different edge types:
    :class:`LineEdge`, :class:`ArcEdge`, :class:`EllipseEdge` of :class:`SplineEdge`.
    Make sure there are no gaps between edges and the edge path must be closed
    to be recognized as path. AutoCAD is very picky in this regard.
    `Ezdxf` performs no checks on gaps between the edges and does not prevent
    creating open loops.

    .. note::

        :class:`ArcEdge` and :class:`EllipseEdge` are ALWAYS represented in
        counter-clockwise orientation, even if an clockwise oriented edge is
        required to build a closed loop. To add a clockwise oriented curve swap
        start- and end angles and set the `ccw` flag to `False` and `ezdxf`
        will export a correct clockwise orientated curve.

    .. attribute:: type

        Path type as :attr:`BoundaryPathType.EDGE` enum

    .. attribute:: path_type_flags

        (bit coded flags)

        === ==============
        0   default
        1   external
        16  outermost
        === ==============

        see :attr:`PolylinePath.path_type_flags`

    .. attribute:: edges

        List of boundary edges of type :class:`LineEdge`, :class:`ArcEdge`,
        :class:`EllipseEdge` of :class:`SplineEdge`

    .. attribute:: source_boundary_objects

        Required for associative hatches, list of handles to the associated DXF
        entities.

    .. automethod:: clear

    .. automethod:: add_line

    .. automethod:: add_arc

    .. automethod:: add_ellipse

    .. automethod:: add_spline


.. class:: EdgeType

    .. attribute:: LINE

    .. attribute:: ARC

    .. attribute:: ELLIPSE

    .. attribute:: SPLINE


.. class:: LineEdge

    Straight boundary edge.

    .. attribute:: type

        Edge type as :attr:`EdgeType.LINE` enum

    .. attribute:: start

        Start point as (x, y)-tuple. (read/write)

    .. attribute:: end

        End point as (x, y)-tuple. (read/write)


.. class:: ArcEdge

    Arc as boundary edge in counter-clockwise orientation,
    see :meth:`EdgePath.add_arc`.

    .. attribute:: type

        Edge type as :attr:`EdgeType.ARC` enum

    .. attribute:: center

        Center point of arc as (x, y)-tuple. (read/write)

    .. attribute:: radius

        Arc radius as float. (read/write)

    .. attribute:: start_angle

        Arc start angle in counter-clockwise orientation in degrees. (read/write)

    .. attribute:: end_angle

        Arc end angle in counter-clockwise orientation in degrees. (read/write)

    .. attribute:: ccw

        ``True`` for counter clockwise arc else ``False``. (read/write)


.. class:: EllipseEdge

    Elliptic arc as boundary edge in counter-clockwise orientation,
    see :meth:`EdgePath.add_ellipse`.

    .. attribute:: type

        Edge type as :attr:`EdgeType.ELLIPSE` enum

    .. attribute:: major_axis_vector

        Ellipse major axis vector as (x, y)-tuple. (read/write)

    .. attribute:: minor_axis_length

        Ellipse minor axis length as float. (read/write)

    .. attribute:: radius

        Ellipse radius as float. (read/write)

    .. attribute:: start_angle

        Ellipse start angle in counter-clockwise orientation in degrees. (read/write)

    .. attribute:: end_angle

        Ellipse end angle in counter-clockwise orientation in degrees. (read/write)

    .. attribute:: ccw

        ``True`` for counter clockwise ellipse else ``False``. (read/write)


.. class:: SplineEdge

    Spline as boundary edge.

    .. attribute:: type

        Edge type as :attr:`EdgeType.SPLINE` enum

    .. attribute:: degree

        Spline degree as int. (read/write)

    .. attribute:: rational

        1 for rational spline else 0. (read/write)

    .. attribute:: periodic

        1 for periodic spline else 0. (read/write)

    .. attribute:: knot_values

        List of knot values as floats. (read/write)

    .. attribute:: control_points

        List of control points as (x, y)-tuples. (read/write)

    .. attribute:: fit_points

        List of fit points as (x, y)-tuples. (read/write)

    .. attribute:: weights

        List of weights (of control points) as floats. (read/write)

    .. attribute:: start_tangent

        Spline start tangent (vector) as (x, y)-tuple. (read/write)

    .. attribute:: end_tangent

        Spline end tangent (vector)  as (x, y)-tuple. (read/write)


Hatch Pattern Definition Classes
--------------------------------

.. class:: Pattern

    .. attribute:: lines

        List of pattern definition lines (read/write). see :class:`PatternLine`

    .. automethod:: add_line

    .. automethod:: clear

    .. automethod:: scale


.. class:: PatternLine

    Represents a pattern definition line, use factory function :meth:`Pattern.add_line`
    to create new pattern definition lines.

    .. attribute:: angle

        Line angle in degrees. (read/write)

    .. attribute:: base_point

        Base point as (x, y)-tuple. (read/write)

    .. attribute:: offset

        Offset as (x, y)-tuple. (read/write)

    .. attribute:: dash_length_items

        List of dash length items (item > 0 is line, < 0 is gap, 0.0 = dot). (read/write)

Hatch Gradient Fill Class
-------------------------

.. class:: Gradient

    .. attribute:: color1

        First rgb color as (r, g, b)-tuple, rgb values in range 0 to 255. (read/write)

    .. attribute:: color2

        Second rgb color as (r, g, b)-tuple, rgb values in range 0 to 255. (read/write)

    .. attribute:: one_color

        If :attr:`one_color` is 1 - the hatch is filled with a smooth transition between
        :attr:`color1` and a specified :attr:`tint` of :attr:`color1`. (read/write)

    .. attribute:: rotation

        Gradient rotation in degrees. (read/write)

    .. attribute:: centered

        Specifies a symmetrical gradient configuration. If this option is not
        selected, the gradient fill is shifted up and to the left, creating the
        illusion of a light source to the left of the object. (read/write)

    .. attribute:: tint

        Specifies the tint (:attr:`color1` mixed with white) of a color to be
        used for a gradient fill of one color. (read/write)

.. seealso::

    :ref:`tut_hatch_pattern`

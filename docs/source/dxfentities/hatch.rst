Hatch
=====

.. module:: ezdxf.entities
    :noindex:

The HATCH entity (`DXF Reference`_) fills an enclosed area defined by one or more boundary paths with a
hatch pattern, solid fill, or gradient fill.

All points in :ref:`OCS` as (x, y) tuples (:attr:`Hatch.dxf.elevation` is the z-axis value).

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'HATCH'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_hatch`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. seealso::

    :ref:`tut_hatch`

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-C6C71CED-CE0F-4184-82A5-07AD6241F15B

.. rubric:: Boundary paths helper classes

Path manager: :class:`BoundaryPaths`

- :class:`PolylinePath`
- :class:`EdgePath`
    - :class:`LineEdge`
    - :class:`ArcEdge`
    - :class:`EllipseEdge`
    - :class:`SplineEdge`

.. rubric:: Pattern and gradient helper classes

- :class:`Pattern`
- :class:`PatternLine`
- :class:`Gradien`

.. class:: Hatch

    .. attribute:: dxf.pattern_name

        Pattern name as string

    .. attribute:: Hatch.dxf.solid_fill

        === ==========================================================
        1   solid fill, better use: :meth:`Hatch.set_solid_fill`
        0   pattern fill, better use: :meth:`Hatch.set_pattern_fill`
        === ==========================================================

    .. attribute:: dxf.associative

        === =========================
        1   associative hatch
        0   not associative hatch
        === =========================

        Associations not handled by `ezdxf`, you have to set the handles to the associated DXF entities by yourself.

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
        2   custom (???)
        === ===================

    .. attribute:: dxf.pattern_angle

        Pattern angle in degrees. (float)

    .. attribute:: dxf.pattern_scale

        Pattern scaling factor. (float)

    .. attribute:: dxf.pattern_double

        ``1`` = double pattern size else ``0``. (int)

    .. attribute:: dxf.n_seed_points

        Count of seed points (better user: :meth:`get_seed_points`)

    .. attribute:: dxf.elevation

       Z value represents the elevation height of the :ref:`OCS`. (float)

    .. attribute:: paths

        :class:`BoundaryPaths` object.

    .. attribute:: pattern

        :class:`Pattern` object.

    .. attribute:: gradient

        :class:`Gradient` object.

    .. attribute:: seeds

        List of ``(x, y)`` tuples.

    .. autoattribute:: has_solid_fill

    .. autoattribute:: has_pattern_fill

    .. autoattribute:: has_gradient_data

    .. autoattribute:: bgcolor

    .. automethod:: edit_boundary() -> BoundaryPaths

    .. automethod:: edit_pattern() -> Pattern

    .. automethod:: set_pattern_definition

    .. automethod:: set_solid_fill

    .. automethod:: set_pattern_fill

    .. automethod:: set_gradient

    .. automethod:: get_gradient

    .. automethod:: edit_gradient

    .. automethod:: get_seed_points

    .. automethod:: set_seed_points



Hatch Boundary Helper Classes
-----------------------------

.. class:: BoundaryPaths

    Defines the borders of the hatch, a hatch can consist of more than one path.

    .. attribute:: paths

        List of all boundary paths. Contains :class:`PolylinePath` and :class:`EdgePath` objects. (read/write)

    .. automethod:: add_polyline_path(path_vertices, is_closed=1, flags=1) -> PolylinePath

    .. automethod:: add_edge_path(flags=1) -> EdgePath

    .. automethod:: clear

.. class:: PolylinePath

    A polyline as hatch boundary path.

    .. attribute:: path_type_flags

        (bit coded flags)

        === ====================================
        0   default
        1   external
        2   polyline, will be set by `ezdxf`
        16  outermost
        === ====================================

        My interpretation of the :attr:`path_type_flags`, see also :ref:`tut_hatch`:

            * external - path is part of the hatch outer border
            * outermost - path is completely inside of one or more external paths
            * default - path is completely inside of one or more outermost paths

        If there are troubles with AutoCAD, maybe the hatch entity has the :attr:`Hatch.dxf.pixel_size` attribute set -
        delete it :code:`del hatch.dxf.pixel_size` and maybe the problem is solved. `ezdxf` does not use the
        :attr:`Hatch.dxf.pixel_size` attribute, but it can occur in DXF files created by other applications.

    .. attribute:: PolylinePath.is_closed

        ``True`` if polyline path is closed.

    .. attribute:: vertices

        List of path vertices as ``(x, y, bulge)`` tuples. (read/write)

    .. attribute:: source_boundary_objects

        List of handles of the associated DXF entities for associative hatches. There is no support for
        associative hatches by `ezdxf`, you have to do it all by yourself. (read/write)

    .. automethod:: set_vertices

    .. automethod:: clear


.. class:: EdgePath

    Boundary path build by edges. There are four different edge types: :class:`LineEdge`, :class:`ArcEdge`,
    :class:`EllipseEdge` of :class:`SplineEdge`. Make sure there are no gaps between edges. AutoCAD in this regard is
    very picky. `ezdxf` performs no checks on gaps between the edges.

    .. attribute:: path_type_flags

        (bit coded flags)

        === ==============
        0   default
        1   external
        16  outermost
        === ==============

        see :attr:`PolylinePath.path_type_flags`

    .. attribute:: edges

        List of boundary edges of type :class:`LineEdge`, :class:`ArcEdge`, :class:`EllipseEdge` of :class:`SplineEdge`

    .. attribute:: source_boundary_objects

        Required for associative hatches, list of handles to the associated DXF entities.

    .. automethod:: clear

    .. automethod:: add_line(start, end) -> LineEdge

    .. automethod:: add_arc(center, radius=1., start_angle=0., end_angle=360., is_counter_clockwise=0) -> ArcEdge

    .. automethod:: add_ellipse(center, major_axis_vector=(1., 0.), minor_axis_length=1., start_angle=0., end_angle=360., is_counter_clockwise=0) -> EllipsePath

    .. automethod:: add_spline(fit_points=None, control_points=None, knot_values=None, weights=None, degree=3, rational=0, periodic=0) -> SplinePath


.. class:: LineEdge

    Straight boundary edge.

    .. attribute:: start

        Start point as ``(x, y)`` tuple. (read/write)

    .. attribute:: end

        End point as ``(x, y)`` tuple. (read/write)


.. class:: ArcEdge

    Arc as boundary edge.

    .. attribute:: center

        Center point of arc as ``(x, y)`` tuple. (read/write)

    .. attribute:: radius

        Arc radius as float. (read/write)

    .. attribute:: start_angle

        Arc start angle in degrees. (read/write)

    .. attribute:: end_angle

        Arc end angle in degrees. (read/write)

    .. attribute:: is_counter_clockwise

        ``1`` for counter clockwise arc else ``0``. (read/write)


.. class:: EllipseEdge

    Elliptic arc as boundary edge.

    .. attribute:: major_axis_vector

        Ellipse major axis vector as ``(x, y)`` tuple. (read/write)

    .. attribute:: minor_axis_length

        Ellipse minor axis length as float. (read/write)

    .. attribute:: radius

        Ellipse radius as float. (read/write)

    .. attribute:: start_angle

        Ellipse start angle in degrees. (read/write)

    .. attribute:: end_angle

        Ellipse end angle in degrees. (read/write)

    .. attribute:: is_counter_clockwise

        ``1`` for counter clockwise ellipse else ``0``. (read/write)


.. class:: SplineEdge

    Spline as boundary edge.

    .. attribute:: degree

        Spline degree as int. (read/write)

    .. attribute:: rational

        ``1`` for rational spline else ``0``. (read/write)

    .. attribute:: periodic

        ``1`` for periodic spline else ``0``. (read/write)

    .. attribute:: knot_values

        List of knot values as floats. (read/write)

    .. attribute:: control_points

        List of control points as ``(x, y)`` tuples. (read/write)

    .. attribute:: fit_points

        List of fit points as ``(x, y)`` tuples. (read/write)

    .. attribute:: weights

        List of weights (of control points) as floats. (read/write)

    .. attribute:: start_tangent

        Spline start tangent (vector) as ``(x, y)`` tuple. (read/write)

    .. attribute:: end_tangent

        Spline end tangent (vector)  as ``(x, y)`` tuple. (read/write)


Hatch Pattern Definition Helper Classes
---------------------------------------

.. class:: Pattern

    .. attribute:: lines

        List of pattern definition lines (read/write). see :class:`PatternLine`

    .. automethod:: add_line

    .. automethod:: new_line

    .. automethod:: clear


.. class:: PatternLine

    Represents a pattern definition line, use factory function :meth:`Pattern.add_line` to create new pattern
    definition lines.

    .. attribute:: angle

        Line angle in degrees. (read/write)

    .. attribute:: base_point

        Base point as ``(x, y)`` tuple. (read/write)

    .. attribute:: offset

        Offset as ``(x, y)`` tuple. (read/write)

    .. attribute:: dash_length_items

        List of dash length items (item > ``0`` is line, < ``0`` is gap, ``0.0`` = dot). (read/write)

Hatch Gradient Fill Helper Classes
----------------------------------

.. class:: Gradient

    .. attribute:: color1

        First rgb color as ``(r, g, b)`` tuple, rgb values in range 0 to 255. (read/write)

    .. attribute:: color2

        Second rgb color as ``(r, g, b)`` tuple, rgb values in range 0 to 255. (read/write)

    .. attribute:: one_color

        If :attr:`one_color` is ``1`` - the hatch is filled with a smooth transition between
        :attr:`color1` and a specified :attr:`tint` of :attr:`color1`. (read/write)

    .. attribute:: rotation

        Gradient rotation in degrees. (read/write)

    .. attribute:: centered

        Specifies a symmetrical gradient configuration. If this option is not selected, the gradient
        fill is shifted up and to the left, creating the illusion of a light source to the left of
        the object. (read/write)

    .. attribute:: tint

        Specifies the tint (:attr:`color1` mixed with white) of a color to be used for a gradient
        fill of one color. (read/write)

.. seealso::

    :ref:`tut_hatch_pattern`

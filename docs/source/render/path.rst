.. module:: ezdxf.render.path

Path
====

This module implements a geometrical :class:`Path` supported by several render
backends, with the goal to create such paths from LWPOLYLINE, POLYLINE and HATCH
boundary paths and send them to the render backend, see :mod:`ezdxf.addons.drawing`.

Minimum common interface:

- matplotlib: `PathPatch`_
    - matplotlib.path.Path() codes:
    - MOVETO
    - LINETO
    - CURVE3 - quadratic Bèzier-curve
    - CURVE4 - cubic Bèzier-curve

- PyQt: `QPainterPath`_
    - moveTo()
    - lineTo()
    - quadTo() - quadratic Bèzier-curve
    - cubicTo() - cubic Bèzier-curve

- PyCairo: `Context`_
    - move_to()
    - line_to()
    - no support for quadratic Bèzier-curve
    - curve_to() - cubic Bèzier-curve

- SVG: `SVG-Path`_
    - "M" - absolute move to
    - "L" - absolute line to
    - "Q" - absolute quadratic Bèzier-curve
    - "C" - absolute cubic Bèzier-curve

ARC and ELLIPSE entities are approximated by multiple cubic Bézier-curves, which
are close enough for display rendering. Non-rational SPLINES of 3rd degree can
be represented exact as multiple cubic Bézier-curves, other B-splines will be
approximated. XLINE and RAY are unsupported linear entities because of their
infinite nature.

.. hint::

    A :class:`Path` can not represent a point. A :class:`Path` with only a
    start point yields no vertices!

.. autofunction:: has_path_support

.. autofunction:: make_path

.. class:: Path

    .. autoattribute:: start

    .. autoattribute:: end

    .. autoattribute:: is_closed

    .. automethod:: control_vertices

    .. automethod:: has_clockwise_orientation

    .. automethod:: line_to(location: Vec3)

    .. automethod:: curve3_to(location: Vec3, ctrl: Vec3)

    .. automethod:: curve4_to(location: Vec3, ctrl1: Vec3, ctrl2: Vec3)

    .. automethod:: close

    .. automethod:: clone() -> Path

    .. automethod:: reversed() -> Path

    .. automethod:: clockwise() -> Path

    .. automethod:: counter_clockwise() -> Path

    .. automethod:: add_curves3(curves: Iterable[Bezier3P])

    .. automethod:: add_curves4(curves: Iterable[Bezier4P])

    .. automethod:: add_ellipse(ellipse: ConstructionEllipse, segments=1)

    .. automethod:: add_spline(spline: BSpline, level=4)

    .. automethod:: add_2d_polyline(points, close: bool, ocs: OCS, elevation: float)

    .. automethod:: transform(m: Matrix44) -> Path

    .. automethod:: approximate(segments: int=20) -> Iterable[Vec3]

    .. automethod:: flattening(distance: float, segments: int=16) -> Iterable[Vec3]

    .. automethod:: from_hatch_boundary_path(boundary: Union[PolylinePath, EdgePath], ocs: OCS = None, elevation: float = 0) -> Path

    .. automethod:: from_hatch_polyline_path(polyline: PolylinePath, ocs: OCS = None, elevation: float = 0) -> Path

    .. automethod:: from_hatch_edge_path(edge: EdgePath, ocs: OCS = None, elevation: float = 0) -> Path

    .. automethod:: from_lwpolyline

    .. automethod:: from_polyline

    .. automethod:: from_spline

    .. automethod:: from_ellipse

    .. automethod:: from_arc

    .. automethod:: from_circle

.. _PathPatch: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.PathPatch.html#matplotlib.patches.PathPatch
.. _QPainterPath: https://doc.qt.io/qt-5/qpainterpath.html
.. _SVG-Path: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
.. _Context: https://pycairo.readthedocs.io/en/latest/reference/context.html
.. _math utilities:

.. module:: ezdxf.math

Utility functions and classes located in module :mod:`ezdxf.math`.

Functions
=========

.. autofunction:: is_close_points

.. autofunction:: closest_point

.. autofunction:: bspline_control_frame

.. autofunction:: bspline_control_frame_approx

.. autofunction:: uniform_knot_vector

.. autofunction:: open_uniform_knot_vector

.. autofunction:: required_knot_values

.. autofunction:: xround

.. autofunction:: linspace

.. _bulge_related_functions:

Bulge Related Functions
-----------------------

.. seealso::

    Description of the :ref:`bulge value`.

.. autofunction:: bulge_center

.. autofunction:: bulge_radius

.. autofunction:: arc_to_bulge

.. autofunction:: bulge_to_arc

.. autofunction:: bulge_3_points

2D Functions
============

.. autofunction:: distance_point_line_2d(point: Vec2, start: Vec2, end: Vec2) -> float

.. autofunction:: point_to_line_relation(point: Vec2, start: Vec2, end: Vec2, abs_tol=1e-10) -> int

.. autofunction:: is_point_on_line_2d(point: Vec2, start: Vec2, end: Vec2, ray=True, abs_tol=1e-10) -> bool

.. autofunction:: is_point_left_of_line(point: Vec2, start: Vec2, end: Vec2, colinear=False) -> bool

.. autofunction:: is_point_in_polygon_2d(point: Vec2, polygon: Iterable[Vec2], abs_tol=1e-10) -> int

.. autofunction:: convex_hull_2d

.. autofunction:: intersection_line_line_2d(line1: Sequence[Vec2], line2: Sequence[Vec2], virtual=True, abs_tol=1e-10) -> Optional[Vec2]

.. autofunction:: rytz_axis_construction(d1: Vector, d2: Vector) -> Tuple[Vector, Vector, float]

.. autofunction:: offset_vertices_2d

.. code-block:: Python

    source = [(0, 0), (3, 0), (3, 3), (0, 3)]
    result = list(offset_vertices_2d(source, offset=0.5, closed=True))

.. image:: gfx/offset_vertices_2d_1.png

Example for a closed collinear shape, which creates 2 additional vertices and the first one has an unexpected location:

.. code-block:: Python

    source = [(0, 0), (0, 1), (0, 2), (0, 3)]
    result = list(offset_vertices_2d(source, offset=0.5, closed=True))

.. image:: gfx/offset_vertices_2d_2.png

3D Functions
============

.. autofunction:: normal_vector_3p(a: Vector, b: Vector, c: Vector) -> Vector

.. autofunction:: is_planar_face(face: Sequence[Vector], abs_tol=1e-9) -> bool

.. autofunction:: subdivide_face(face: Sequence[Union[Vector, Vec2]], quads=True) -> Iterable[List[Vector]]

.. autofunction:: subdivide_ngons(faces: Iterable[Sequence[Union[Vector, Vec2]]]) -> Iterable[List[Vector]]

.. autofunction:: intersection_ray_ray_3d(ray1: Tuple[Vector, Vector], ray2: Tuple[Vector, Vector], abs_tol=1e-10) -> Sequence[Vector]

.. autofunction:: rational_spline_from_arc(center: Vector = (0, 0), radius:float=1, start_angle: float = 0, end_angle: float = 360, segments: int = 1) -> BSpline

.. autofunction:: rational_spline_from_ellipse(ellipse: ConstructionEllipse, segments: int = 1) -> BSpline

.. autofunction:: bezier4p_from_arc(center: Vector = (0, 0), radius:float=1, start_angle: float = 0, end_angle: float = 360, segments: int = 1) -> Iterable[Bezier4P]

.. autofunction:: bezier4p_from_ellipse(ellipse: ConstructionEllipse, segments: int = 1) -> Iterable[Bezier4P]

.. autofunction:: bezier4p_interpolation(points: Iterable[Vertex]) -> List[Bezier4P]

Transformation Classes
======================

OCS Class
---------

.. autoclass:: OCS

    .. autoattribute:: ux

    .. autoattribute:: uy

    .. autoattribute:: uz

    .. automethod:: from_wcs

    .. automethod:: points_from_wcs

    .. automethod:: to_wcs

    .. automethod:: points_to_wcs

    .. automethod:: render_axis


UCS Class
---------

.. autoclass:: UCS

    .. autoattribute:: ux

    .. autoattribute:: uy

    .. autoattribute:: uz

    .. autoattribute:: is_cartesian

    .. automethod:: copy() -> UCS

    .. automethod:: to_wcs

    .. automethod:: points_to_wcs

    .. automethod:: direction_to_wcs

    .. automethod:: from_wcs

    .. automethod:: points_from_wcs

    .. automethod:: direction_from_wcs

    .. automethod:: to_ocs

    .. automethod:: points_to_ocs

    .. automethod:: to_ocs_angle_deg

    .. automethod:: rotate(axis: Vertex, angle:float) -> UCS

    .. automethod:: rotate_local_x(angle:float) -> UCS

    .. automethod:: rotate_local_y(angle:float) -> UCS

    .. automethod:: rotate_local_z(angle:float) -> UCS

    .. automethod:: shift(delta: Vertex) -> UCS

    .. automethod:: moveto(location: Vertex) -> UCS

    .. automethod:: from_x_axis_and_point_in_xy

    .. automethod:: from_x_axis_and_point_in_xz

    .. automethod:: from_y_axis_and_point_in_xy

    .. automethod:: from_y_axis_and_point_in_yz

    .. automethod:: from_z_axis_and_point_in_xz

    .. automethod:: from_z_axis_and_point_in_yz

    .. automethod:: render_axis


Matrix44
--------

.. autoclass:: Matrix44

    .. automethod:: __repr__

    .. automethod:: set

    .. automethod:: get_row

    .. automethod:: set_row

    .. automethod:: get_col

    .. automethod:: set_col

    .. automethod:: copy() -> Matrix44

    .. automethod:: __copy__() -> Matrix44

    .. automethod:: scale(sx: float, sy: float = None, sz: float = None) -> Matrix44

    .. automethod:: translate(dx: float, dy: float, dz: float) -> Matrix44

    .. automethod:: x_rotate(angle: float) -> Matrix44

    .. automethod:: y_rotate(angle: float) -> Matrix44

    .. automethod:: z_rotate(angle: float) -> Matrix44

    .. automethod:: axis_rotate(axis: Vertex, angle: float) -> Matrix44

    .. automethod:: xyz_rotate(angle_x: float, angle_y: float, angle_z: float) -> Matrix44

    .. automethod:: perspective_projection(left: float, right: float, top: float, bottom: float, near: float, far: float) -> Matrix44

    .. automethod:: perspective_projection_fov(fov: float, aspect: float, near: float, far: float) -> Matrix44

    .. automethod:: chain(*matrices: Iterable[Matrix44]) -> Matrix44

    .. automethod:: ucs(ux: Vertex, uy: Vertex, uz: Vertex) -> Matrix44

    .. automethod:: __hash__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __iter__

    .. automethod:: rows

    .. automethod:: columns

    .. automethod:: __mul__(other: Matrix44) -> Matrix44

    .. automethod:: __imul__(other: Matrix44) -> Matrix44

    .. automethod:: fast_mul(other: Matrix44) -> Matrix44

    .. automethod:: transform

    .. automethod:: transform_direction

    .. automethod:: transform_vertices

    .. automethod:: transform_directions

    .. automethod:: transpose

    .. automethod:: determinant

    .. automethod:: inverse

Construction Tools
==================

Vector
------

.. autoclass:: Vector

    .. autoattribute:: x

    .. autoattribute:: y

    .. autoattribute:: z

    .. autoattribute:: xy

    .. autoattribute:: xyz

    .. autoattribute:: vec2

    .. autoattribute:: magnitude

    .. autoattribute:: magnitude_xy

    .. autoattribute:: magnitude_square

    .. autoattribute:: is_null

    .. autoattribute:: angle

    .. autoattribute:: angle_deg

    .. autoattribute:: spatial_angle

    .. autoattribute:: spatial_angle_deg

    .. automethod:: __str__

    .. automethod:: __repr__

    .. automethod:: __len__

    .. automethod:: __hash__

    .. automethod:: copy() -> Vector

    .. automethod:: __copy__() -> Vector

    .. automethod:: __deepcopy__(memodict: dict) -> Vector

    .. automethod:: __getitem__

    .. automethod:: __iter__

    .. automethod:: __abs__

    .. automethod:: replace(x: float = None, y: float = None, z: float = None) -> Vector

    .. automethod:: generate(items: Iterable[Vertex]) -> Iterable[Vector]

    .. automethod:: list(items: Iterable[Vertex]) -> List[Vector]

    .. automethod:: from_angle(angle: float, length: float = 1.) -> Vector

    .. automethod:: from_deg_angle(angle: float, length: float = 1.) -> Vector

    .. automethod:: orthogonal(ccw: bool = True) -> Vector

    .. automethod:: lerp(other: Any, factor=.5) -> Vector

    .. automethod:: is_parallel(other: Vector, abs_tolr=1e-12) -> bool

    .. automethod:: project(other: Any) -> Vector

    .. automethod:: normalize(length: float = 1.) -> Vector

    .. automethod:: reversed() -> Vector

    .. automethod:: isclose

    .. automethod:: __neg__() -> Vector

    .. automethod:: __bool__

    .. automethod:: __eq__

    .. automethod:: __lt__

    .. automethod:: __add__(other: Any) -> Vector

    .. automethod:: __radd__(other: Any) -> Vector

    .. automethod:: __sub__(other: Any) -> Vector

    .. automethod:: __rsub__(other: Any) -> Vector

    .. automethod:: __mul__(other: float) -> Vector

    .. automethod:: __rmul__(other: float) -> Vector

    .. automethod:: __truediv__(other: float) -> Vector

    .. automethod:: __div__(other: float) -> Vector

    .. automethod:: __rtruediv__(other: float) -> Vector

    .. automethod:: __rdiv__(other: float) -> Vector

    .. automethod:: dot

    .. automethod:: cross(other: Any) -> Vector

    .. automethod:: distance

    .. automethod:: angle_about(base: Vector, target: Vector) -> float

    .. automethod:: angle_between

    .. automethod:: rotate(angle: float) -> Vector

    .. automethod:: rotate_deg(angle: float) -> Vector

.. attribute:: X_AXIS

    :code:`Vector(1, 0, 0)`

.. attribute:: Y_AXIS

    :code:`Vector(0, 1, 0)`

.. attribute:: Z_AXIS

    :code:`Vector(0, 0, 1)`

.. attribute:: NULLVEC

    :code:`Vector(0, 0, 0)`

Vec2
----

.. autoclass:: Vec2(v)

Plane
-----

.. autoclass:: Plane(normal: Vector, distance: float)

    .. autoattribute:: normal

    .. autoattribute:: distance_from_origin

    .. autoattribute:: vector

    .. automethod:: from_3p(a: Vector, b: Vector, c: Vector) -> Plane

    .. automethod:: from_vector(vector) -> Plane

    .. automethod:: copy() -> Plane

    .. automethod:: signed_distance_to(v: Vector) -> float

    .. automethod:: distance_to(v: Vector) -> float

    .. automethod:: is_coplanar_vertex(v: Vector, abs_tol=1e-9) -> bool

    .. automethod:: is_coplanar_plane(p: Plane, abs_tol=1e-9) -> bool


BoundingBox
-----------

.. autoclass:: BoundingBox
    :members:

    .. attribute:: extmin

        "lower left" corner of bounding box

    .. attribute:: extmax

        "upper right" corner of bounding box


BoundingBox2d
-------------

.. autoclass:: BoundingBox2d
    :members:

    .. attribute:: extmin

        "lower left" corner of bounding box

    .. attribute:: extmax

        "upper right" corner of bounding box

ConstructionRay
---------------

.. autoclass:: ConstructionRay

    .. autoattribute:: location

    .. autoattribute:: direction

    .. autoattribute:: slope

    .. autoattribute:: angle

    .. autoattribute:: angle_deg

    .. autoattribute:: is_vertical

    .. autoattribute:: is_horizontal

    .. automethod:: __str__

    .. automethod:: is_parallel(self, other: ConstructionRay) -> bool

    .. automethod:: intersect(other: ConstructionRay) -> Vec2

    .. automethod:: orthogonal(location: 'Vertex') -> ConstructionRay

    .. automethod:: bisectrix(other: ConstructionRay) -> ConstructionRay:

    .. automethod:: yof

    .. automethod:: xof

ConstructionLine
----------------

.. autoclass:: ConstructionLine

    .. attribute:: start

        start point as :class:`Vec2`

    .. attribute:: end

        end point as :class:`Vec2`

    .. autoattribute:: bounding_box

    .. autoattribute:: ray

    .. autoattribute:: is_vertical

    .. automethod:: __str__

    .. automethod:: translate

    .. automethod:: length

    .. automethod:: midpoint() -> Vec2

    .. automethod:: inside_bounding_box

    .. automethod:: intersect(other: ConstructionLine, abs_tol:float=1e-10) -> Optional[Vec2]

    .. automethod:: has_intersection(other: ConstructionLine, abs_tol:float=1e-10) -> bool

    .. automethod:: is_point_left_of_line


ConstructionCircle
------------------

.. autoclass:: ConstructionCircle

    .. attribute:: center

        center point as :class:`Vec2`

    .. attribute:: radius

        radius as float

    .. autoattribute:: bounding_box

    .. automethod:: from_3p(p1: Vertex, p2: Vertex, p3: Vertex) -> ConstructionCircle

    .. automethod:: __str__

    .. automethod:: translate

    .. automethod:: point_at(angle: float) -> Vec2

    .. automethod:: inside

    .. automethod:: tangent(angle: float) -> ConstructionRay

    .. automethod:: intersect_ray(ray: ConstructionRay, abs_tol: float = 1e-10) -> Sequence[Vec2]

    .. automethod:: intersect_circle(other: ConstructionCircle, abs_tol: float = 1e-10) -> Sequence[Vec2]

ConstructionArc
---------------

.. autoclass:: ConstructionArc

    .. attribute:: center

        center point as :class:`Vec2`

    .. attribute:: radius

        radius as float

    .. attribute:: start_angle

        start angle in degrees

    .. attribute:: end_angle

        end angle in degrees

    .. autoattribute:: start_angle_rad

    .. autoattribute:: end_angle_rad

    .. autoattribute:: start_point

    .. autoattribute:: end_point

    .. autoattribute:: bounding_box

    .. automethod:: angles

    .. automethod:: vertices

    .. automethod:: tangents

    .. automethod:: translate(dx: float, dy: float) -> ConstructionArc

    .. automethod:: scale_uniform(s: float) -> ConstructionArc

    .. automethod:: rotate_z(angle: float) -> ConstructionArc

    .. automethod:: from_2p_angle(start_point: Vertex, end_point: Vertex, angle: float, ccw: bool = True) -> ConstructionArc

    .. automethod:: from_2p_radius(start_point: Vertex, end_point: Vertex, radius: float, ccw: bool = True,  center_is_left: bool = True) -> ConstructionArc

    .. automethod:: from_3p(start_point: Vertex, end_point: Vertex, def_point: Vertex, ccw: bool = True) -> ConstructionArc

    .. automethod:: add_to_layout(layout: BaseLayout, ucs: UCS = None, dxfattribs: dict = None) -> Arc

ConstructionEllipse
-------------------

.. autoclass:: ConstructionEllipse

    .. attribute:: center

        center point as :class:`Vector`

    .. attribute:: major_axis

        major axis as :class:`Vector`

    .. attribute:: minor_axis

        minor axis as :class:`Vector`, automatically calculated from
        :attr:`major_axis` and :attr:`extrusion`.

    .. attribute:: extrusion

        extrusion vector (normal of ellipse plane) as :class:`Vector`

    .. attribute:: ratio

        ratio of minor axis to major axis (float)

    .. attribute:: start

        start param in radians (float)

    .. attribute:: end

        end param in radians (float)

    .. autoattribute:: start_point

    .. autoattribute:: end_point

    .. automethod:: to_ocs() -> ConstructionEllipse

    .. automethod:: params

    .. automethod:: vertices

    .. automethod:: params_from_vertices

    .. automethod:: dxfattribs

    .. automethod:: main_axis_points

    .. automethod:: from_arc(center: Vertex=(0, 0, 0), radius: float = 1, extrusion: Vertex=(0, 0, 1), start_angle: float = 0, end_angle: float = 360, ccw: bool = True) -> ConstructionEllipse

    .. automethod:: transform(m: Matrix44)

    .. automethod:: swap_axis

    .. automethod:: add_to_layout(layout: BaseLayout, dxfattribs: dict = None) -> Ellipse


ConstructionBox
---------------

.. autoclass:: ConstructionBox

    .. autoattribute:: center

    .. autoattribute:: width

    .. autoattribute:: height

    .. autoattribute:: angle

    .. autoattribute:: corners

    .. autoattribute:: bounding_box

    .. autoattribute:: incircle_radius

    .. autoattribute:: circumcircle_radius

    .. automethod:: __iter__() -> Iterable[Vec2]

    .. automethod:: __getitem__(corner) -> Vec2

    .. automethod:: __repr__

    .. automethod:: from_points(p1: Vertex, p2: Vertex) -> ConstructionBox

    .. automethod:: translate

    .. automethod:: expand

    .. automethod:: scale

    .. automethod:: rotate

    .. automethod:: is_inside

    .. automethod:: is_any_corner_inside(other: ConstructionBox) -> bool

    .. automethod:: is_overlapping(other: ConstructionBox) -> bool

    .. automethod:: border_lines() -> Sequence[ConstructionLine]

    .. automethod:: intersect(line: ConstructionLine) -> List[Vec2]

Shape2d
-------

.. autoclass:: Shape2d

    .. attribute:: vertices

        List of :class:`Vec2` objects

    .. autoattribute:: bounding_box

    .. automethod:: __len__

    .. automethod:: __getitem__(item) -> Vec2

    .. automethod:: append

    .. automethod:: extend

    .. automethod:: translate

    .. automethod:: scale

    .. automethod:: scale_uniform

    .. automethod:: rotate

    .. automethod:: rotate_rad

    .. automethod:: offset

    .. automethod:: convex_hull

Curves
======

BSpline
-------

.. autoclass:: BSpline

    .. attribute:: control_points

        control points as list of :class:`~ezdxf.math.Vector`

    .. autoattribute:: count

    .. attribute:: degree

    .. attribute:: order

        order of B-spline = degree +  1

    .. autoattribute:: max_t

    .. automethod:: knots

    .. automethod:: weights

    .. automethod:: basis_values

    .. automethod:: point(t: float) -> Vector

    .. automethod:: insert_knot

    .. automethod:: approximate(segments: int = 20) -> Iterable[Vector]

    .. automethod:: from_ellipse(ellipse: ConstructionEllipse) -> BSpline

    .. automethod:: from_arc(arc: ConstructionArc) -> BSpline

    .. automethod:: from_fit_points(points: Iterable[Vertex], degree:int=3) -> BSpline

    .. automethod:: ellipse_approximation(ellipse: ConstructionEllipse, num:int=16) -> BSpline

    .. automethod:: arc_approximation(arc: ConstructionArc, num:int=16) -> BSpline

    .. automethod:: transform(m: Matrix44) -> BSpline

BSplineU
--------

.. autoclass:: BSplineU

BSplineClosed
-------------

.. autoclass:: BSplineClosed


DBSpline
--------

.. autoclass:: DBSpline

    .. automethod:: point(t: float) -> Tuple[Vector, Vector, Vector]

DBSplineU
---------

.. autoclass:: DBSplineU

DBSplineClosed
--------------

.. autoclass:: DBSplineClosed

Bezier
------

.. autoclass:: Bezier

    .. autoattribute:: control_points

    .. automethod:: approximate(segments: int = 20) -> Iterable[Vector]

    .. automethod:: point(t: float) -> Vector

DBezier
-------

.. autoclass:: DBezier

    .. automethod:: point(t: float) -> Tuple[Vector, Vector, Vector]

Bezier4P
--------

.. autoclass:: Bezier4P

    .. autoattribute:: control_points

    .. automethod:: to2d() -> Bezier4P

    .. automethod:: to3d() -> Bezier4P

    .. automethod:: point(t: float) -> Union[Vector, Vec2]

    .. automethod:: tangent(t: float) -> Union[Vector, Vec2]

    .. automethod:: approximate(segments: int) -> Iterable[Union[Vector, Vec2]]

    .. automethod:: approximated_length

BezierSurface
-------------

.. autoclass:: BezierSurface

    .. autoattribute:: nrows

    .. autoattribute:: ncols

    .. automethod:: point

    .. automethod:: approximate


EulerSpiral
-----------

.. autoclass:: EulerSpiral

    .. automethod:: radius

    .. automethod:: tangent(t: float) -> Vector

    .. automethod:: distance

    .. automethod:: point(t: float) -> Vector

    .. automethod:: circle_center(t: float) -> Vector

    .. automethod:: approximate(length: float, segments: int) -> Iterable[Vector]

    .. automethod:: bspline(length: float, segments: int = 10, degree: int = 3, method: str = 'uniform') -> BSpline

.. _Curve Global Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
.. _clamped curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve.html
.. _open curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-open.html
.. _closed curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
.. _basis: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-basis.html
.. _B-spline: https://en.wikipedia.org/wiki/B-spline
.. _Bézier curve: https://en.wikipedia.org/wiki/B%C3%A9zier_curve
.. _Lee Mac: http://www.lee-mac.com/bulgeconversion.html
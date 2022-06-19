.. _math utilities:

.. module:: ezdxf.math

Utility functions and classes located in module :mod:`ezdxf.math`.

Functions
=========

.. autofunction:: closest_point

.. autofunction:: uniform_knot_vector

.. autofunction:: open_uniform_knot_vector

.. autofunction:: required_knot_values

.. autofunction:: xround

.. autofunction:: linspace

.. autofunction:: area

.. autofunction:: arc_angle_span_deg

.. autofunction:: arc_angle_span_rad

.. autofunction:: arc_segment_count

.. autofunction:: arc_chord_length

.. autofunction:: ellipse_param_span

.. autofunction:: has_matrix_2d_stretching

.. autofunction:: has_matrix_3d_stretching

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

.. autofunction:: distance_point_line_2d

.. autofunction:: point_to_line_relation

.. autofunction:: is_point_on_line_2d

.. autofunction:: is_point_left_of_line

.. autofunction:: is_point_in_polygon_2d

.. autofunction:: convex_hull_2d

.. autofunction:: intersection_line_line_2d

.. autofunction:: intersect_polylines_2d

.. autofunction:: rytz_axis_construction

.. autofunction:: clip_polygon_2d

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

.. seealso::

    The free online book `3D Math Primer for Graphics and Game Development <https://gamemath.com/>`_
    is a very good resource for learning vector math and other graphic related topics,
    it is easy to read for beginners and especially targeted to programmers.

.. autofunction:: basic_transformation

.. autofunction:: normal_vector_3p

.. autofunction:: safe_normal_vector

.. autofunction:: linear_vertex_spacing

.. autofunction:: best_fit_normal

.. autofunction:: is_planar_face

.. autofunction:: subdivide_face

.. autofunction:: subdivide_ngons

.. autofunction:: distance_point_line_3d

.. autofunction:: intersection_ray_ray_3d

.. autofunction:: intersection_line_line_3d

.. autofunction:: intersection_ray_polygon_3d

.. autofunction:: intersection_line_polygon_3d

.. autofunction:: intersect_polylines_3d

.. autofunction:: estimate_tangents

.. autofunction:: estimate_end_tangent_magnitude

.. autofunction:: fit_points_to_cad_cv

.. autofunction:: fit_points_to_cubic_bezier

.. autofunction:: global_bspline_interpolation

.. autofunction:: local_cubic_bspline_interpolation

.. autofunction:: rational_bspline_from_arc

.. autofunction:: rational_bspline_from_ellipse

.. autofunction:: open_uniform_bspline

.. autofunction:: closed_uniform_bspline

.. autofunction:: cubic_bezier_from_arc

.. autofunction:: cubic_bezier_from_ellipse

.. autofunction:: cubic_bezier_from_3p

.. autofunction:: cubic_bezier_interpolation

.. autofunction:: quadratic_to_cubic_bezier

.. autofunction:: quadratic_bezier_from_3p

.. autofunction:: bezier_to_bspline

.. autofunction:: have_bezier_curves_g1_continuity

.. autofunction:: split_bezier

.. autofunction:: split_polygon_by_plane

.. autofunction:: spherical_envelope

.. autofunction:: dbscan

.. autofunction:: k_means

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

    .. automethod:: copy

    .. automethod:: to_wcs

    .. automethod:: points_to_wcs

    .. automethod:: direction_to_wcs

    .. automethod:: from_wcs

    .. automethod:: points_from_wcs

    .. automethod:: direction_from_wcs

    .. automethod:: to_ocs

    .. automethod:: points_to_ocs

    .. automethod:: to_ocs_angle_deg

    .. automethod:: transform

    .. automethod:: rotate

    .. automethod:: rotate_local_x

    .. automethod:: rotate_local_y

    .. automethod:: rotate_local_z

    .. automethod:: shift

    .. automethod:: moveto

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

    .. automethod:: get_row

    .. automethod:: set_row

    .. automethod:: get_col

    .. automethod:: set_col

    .. automethod:: copy

    .. automethod:: __copy__

    .. automethod:: scale

    .. automethod:: translate

    .. automethod:: x_rotate

    .. automethod:: y_rotate

    .. automethod:: z_rotate

    .. automethod:: axis_rotate

    .. automethod:: xyz_rotate

    .. automethod:: shear_xy

    .. automethod:: perspective_projection

    .. automethod:: perspective_projection_fov

    .. automethod:: chain

    .. automethod:: ucs

    .. automethod:: __hash__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __iter__

    .. automethod:: rows

    .. automethod:: columns

    .. automethod:: __mul__

    .. automethod:: __imul__

    .. automethod:: transform

    .. automethod:: transform_direction

    .. automethod:: transform_vertices

    .. automethod:: transform_directions

    .. automethod:: transpose

    .. automethod:: determinant

    .. automethod:: inverse

    .. autoproperty:: is_cartesian

    .. autoproperty:: is_orthogonal

Construction Tools
==================

UVec
----

.. class:: UVec

    Type alias for :code:`Union[Sequence[float], Vec2, Vec3]`

Vec3
----

.. autoclass:: Vec3

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

    .. automethod:: copy

    .. automethod:: __copy__

    .. automethod:: __deepcopy__

    .. automethod:: __getitem__

    .. automethod:: __iter__

    .. automethod:: __abs__

    .. automethod:: replace

    .. automethod:: generate

    .. automethod:: list

    .. automethod:: tuple

    .. automethod:: from_angle

    .. automethod:: from_deg_angle

    .. automethod:: orthogonal

    .. automethod:: lerp

    .. automethod:: is_parallel

    .. automethod:: project

    .. automethod:: normalize

    .. automethod:: reversed

    .. automethod:: isclose

    .. automethod:: __neg__

    .. automethod:: __bool__

    .. automethod:: __eq__

    .. automethod:: __lt__

    .. automethod:: __add__

    .. automethod:: __radd__

    .. automethod:: __sub__

    .. automethod:: __rsub__

    .. automethod:: __mul__

    .. automethod:: __rmul__

    .. automethod:: __truediv__

    .. automethod:: dot

    .. automethod:: cross

    .. automethod:: distance

    .. automethod:: angle_about

    .. automethod:: angle_between

    .. automethod:: rotate

    .. automethod:: rotate_deg

    .. automethod:: sum

.. attribute:: X_AXIS

    :code:`Vec3(1, 0, 0)`

.. attribute:: Y_AXIS

    :code:`Vec3(0, 1, 0)`

.. attribute:: Z_AXIS

    :code:`Vec3(0, 0, 1)`

.. attribute:: NULLVEC

    :code:`Vec3(0, 0, 0)`

Vec2
----

.. autoclass:: Vec2


Plane
-----


.. autoclass:: Plane(normal: Vec3, distance: float)

    .. autoattribute:: normal

    .. autoattribute:: distance_from_origin

    .. autoattribute:: vector

    .. automethod:: from_3p

    .. automethod:: from_vector

    .. automethod:: copy

    .. automethod:: signed_distance_to

    .. automethod:: distance_to

    .. automethod:: is_coplanar_vertex

    .. automethod:: is_coplanar_plane

    .. automethod:: intersect_line

    .. automethod:: intersect_ray


BoundingBox
-----------

.. autoclass:: BoundingBox

    .. attribute:: extmin

        "lower left" corner of bounding box

    .. attribute:: extmax

        "upper right" corner of bounding box

    .. autoproperty:: is_empty

    .. autoproperty:: has_data

    .. autoproperty:: size

    .. autoproperty:: center

    .. automethod:: inside

    .. automethod:: any_inside

    .. automethod:: all_inside

    .. automethod:: has_intersection

    .. automethod:: has_overlap

    .. automethod:: contains

    .. automethod:: extend

    .. automethod:: union

    .. automethod:: intersection

    .. automethod:: rect_vertices

    .. automethod:: cube_vertices

    .. automethod:: grow

BoundingBox2d
-------------

.. autoclass:: BoundingBox2d

    .. attribute:: extmin

        "lower left" corner of bounding box

    .. attribute:: extmax

        "upper right" corner of bounding box

    .. autoproperty:: is_empty

    .. autoproperty:: has_data

    .. autoproperty:: size

    .. autoproperty:: center

    .. automethod:: inside

    .. automethod:: any_inside

    .. automethod:: all_inside

    .. automethod:: has_intersection

    .. automethod:: has_overlap

    .. automethod:: contains

    .. automethod:: extend

    .. automethod:: union

    .. automethod:: intersection

    .. automethod:: rect_vertices

RTree
-----

.. autoclass:: RTree(points: Iterable[AnyVec], max_node_size: int = 5)

    .. automethod:: __len__

    .. automethod:: __iter__

    .. automethod:: contains

    .. automethod:: nearest_neighbor

    .. automethod:: points_in_sphere

    .. automethod:: points_in_bbox

    .. automethod:: avg_leaf_size

    .. automethod:: avg_spherical_envelope_radius

    .. automethod:: avg_nn_distance


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

    .. automethod:: is_parallel

    .. automethod:: intersect

    .. automethod:: orthogonal

    .. automethod:: bisectrix

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

    .. autoattribute:: is_horizontal

    .. automethod:: __str__

    .. automethod:: translate

    .. automethod:: length

    .. automethod:: midpoint

    .. automethod:: inside_bounding_box

    .. automethod:: intersect

    .. automethod:: has_intersection

    .. automethod:: is_point_left_of_line


ConstructionCircle
------------------

.. autoclass:: ConstructionCircle

    .. attribute:: center

        center point as :class:`Vec2`

    .. attribute:: radius

        radius as float

    .. autoattribute:: bounding_box

    .. automethod:: from_3p

    .. automethod:: __str__

    .. automethod:: translate

    .. automethod:: point_at

    .. automethod:: vertices

    .. automethod:: flattening

    .. automethod:: inside

    .. automethod:: tangent

    .. automethod:: intersect_ray

    .. automethod:: intersect_line

    .. automethod:: intersect_circle

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

    .. autoattribute:: angle_span

    .. autoattribute:: start_angle_rad

    .. autoattribute:: end_angle_rad

    .. autoattribute:: start_point

    .. autoattribute:: end_point

    .. autoattribute:: bounding_box

    .. automethod:: angles

    .. automethod:: vertices

    .. automethod:: tangents

    .. automethod:: translate

    .. automethod:: scale_uniform

    .. automethod:: rotate_z

    .. automethod:: from_2p_angle

    .. automethod:: from_2p_radius

    .. automethod:: from_3p

    .. automethod:: add_to_layout

    .. automethod:: intersect_ray

    .. automethod:: intersect_line

    .. automethod:: intersect_circle

    .. automethod:: intersect_arc

ConstructionEllipse
-------------------

.. autoclass:: ConstructionEllipse

    .. attribute:: center

        center point as :class:`Vec3`

    .. attribute:: major_axis

        major axis as :class:`Vec3`

    .. attribute:: minor_axis

        minor axis as :class:`Vec3`, automatically calculated from
        :attr:`major_axis` and :attr:`extrusion`.

    .. attribute:: extrusion

        extrusion vector (normal of ellipse plane) as :class:`Vec3`

    .. attribute:: ratio

        ratio of minor axis to major axis (float)

    .. attribute:: start

        start param in radians (float)

    .. attribute:: end

        end param in radians (float)

    .. autoattribute:: start_point

    .. autoattribute:: end_point

    .. autoproperty:: param_span

    .. automethod:: to_ocs

    .. automethod:: params

    .. automethod:: vertices

    .. automethod:: flattening

    .. automethod:: params_from_vertices

    .. automethod:: dxfattribs

    .. automethod:: main_axis_points

    .. automethod:: from_arc

    .. automethod:: transform

    .. automethod:: swap_axis

    .. automethod:: add_to_layout


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

    .. automethod:: __iter__

    .. automethod:: __getitem__

    .. automethod:: __repr__

    .. automethod:: from_points

    .. automethod:: translate

    .. automethod:: expand

    .. automethod:: scale

    .. automethod:: rotate

    .. automethod:: is_inside

    .. automethod:: is_any_corner_inside

    .. automethod:: is_overlapping

    .. automethod:: border_lines

    .. automethod:: intersect

ConstructionPolyline
--------------------

.. autoclass:: ConstructionPolyline

    .. autoproperty:: length

    .. autoproperty:: is_closed

    .. automethod:: data

    .. automethod:: index_at

    .. automethod:: vertex_at

    .. automethod:: divide

    .. automethod:: divide_by_length


Shape2d
-------

.. autoclass:: Shape2d

    .. attribute:: vertices

        List of :class:`Vec2` objects

    .. autoattribute:: bounding_box

    .. automethod:: __len__

    .. automethod:: __getitem__

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

    .. autoproperty:: control_points

    .. autoproperty:: count

    .. autoproperty:: order

    .. autoproperty:: degree

    .. autoproperty:: max_t

    .. autoproperty:: is_rational

    .. autoproperty:: is_clamped

    .. automethod:: knots

    .. automethod:: weights

    .. automethod:: params

    .. automethod:: reverse

    .. automethod:: transform

    .. automethod:: approximate

    .. automethod:: flattening

    .. automethod:: point

    .. automethod:: points

    .. automethod:: derivative

    .. automethod:: derivatives

    .. automethod:: insert_knot

    .. automethod:: knot_refinement

    .. automethod:: from_ellipse

    .. automethod:: from_arc

    .. automethod:: from_fit_points

    .. automethod:: arc_approximation

    .. automethod:: ellipse_approximation

    .. automethod:: bezier_decomposition

    .. automethod:: cubic_bezier_approximation


Bezier
------

.. autoclass:: Bezier

    .. autoattribute:: control_points

    .. automethod:: params

    .. automethod:: reverse

    .. automethod:: transform

    .. automethod:: approximate

    .. automethod:: flattening

    .. automethod:: point

    .. automethod:: points

    .. automethod:: derivative

    .. automethod:: derivatives


Bezier4P
--------

.. autoclass:: Bezier4P

    .. autoattribute:: control_points

    .. automethod:: reverse

    .. automethod:: transform

    .. automethod:: approximate

    .. automethod:: flattening

    .. automethod:: approximated_length

    .. automethod:: point

    .. automethod:: tangent

Bezier3P
--------

.. autoclass:: Bezier3P

    .. autoattribute:: control_points

    .. automethod:: reverse

    .. automethod:: transform

    .. automethod:: approximate

    .. automethod:: flattening

    .. automethod:: approximated_length

    .. automethod:: point

    .. automethod:: tangent

ApproxParamT
------------

.. autoclass:: ApproxParamT(curve, *, max_t: float = 1.0, segments: int = 100)

    .. autoproperty:: max_t

    .. autoproperty:: polyline

    .. automethod:: param_t

    .. automethod:: distance

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

    .. automethod:: tangent

    .. automethod:: distance

    .. automethod:: point

    .. automethod:: circle_center

    .. automethod:: approximate

    .. automethod:: bspline

Linear Algebra
==============

Functions
---------

.. autofunction:: gauss_jordan_solver

.. autofunction:: gauss_jordan_inverse

.. autofunction:: gauss_vector_solver

.. autofunction:: gauss_matrix_solver

.. autofunction:: tridiagonal_vector_solver

.. autofunction:: tridiagonal_matrix_solver

.. autofunction:: banded_matrix

.. autofunction:: detect_banded_matrix

.. autofunction:: compact_banded_matrix

.. autofunction:: freeze_matrix

Matrix Class
------------

.. autoclass:: Matrix

    .. autoattribute:: nrows

    .. autoattribute:: ncols

    .. autoattribute:: shape

    .. automethod:: reshape

    .. automethod:: identity

    .. automethod:: row

    .. automethod:: iter_row

    .. automethod:: col

    .. automethod:: iter_col

    .. automethod:: diag

    .. automethod:: iter_diag

    .. automethod:: rows

    .. automethod:: cols

    .. automethod:: set_row

    .. automethod:: set_col

    .. automethod:: set_diag

    .. automethod:: append_row

    .. automethod:: append_col

    .. automethod:: swap_rows

    .. automethod:: swap_cols

    .. automethod:: transpose

    .. automethod:: inverse

    .. automethod:: determinant

    .. automethod:: freeze

    .. automethod:: lu_decomp

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __eq__

    .. automethod:: __add__

    .. automethod:: __sub__

    .. automethod:: __mul__


LUDecomposition Class
---------------------

.. autoclass:: LUDecomposition

    .. autoattribute:: nrows

    .. automethod:: solve_vector

    .. automethod:: solve_matrix

    .. automethod:: inverse

    .. automethod:: determinant

BandedMatrixLU Class
--------------------

.. autoclass:: BandedMatrixLU

    .. attribute:: upper

        Upper triangle

    .. attribute:: lower

        Lower triangle

    .. attribute:: m1

        Lower band count, excluding main matrix diagonal

    .. attribute:: m2

        Upper band count, excluding main matrix diagonal

    .. attribute:: index

        Swapped indices

    .. autoattribute:: nrows

    .. automethod:: solve_vector

    .. automethod:: solve_matrix

    .. automethod:: determinant

.. _Global Curve Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
.. _clamped curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve.html
.. _open curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-open.html
.. _closed curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
.. _basis: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-basis_vector.html
.. _B-spline: https://en.wikipedia.org/wiki/B-spline
.. _Bézier curve: https://en.wikipedia.org/wiki/B%C3%A9zier_curve
.. _Lee Mac: http://www.lee-mac.com/bulgeconversion.html
.. _Gauss-Jordan: https://en.wikipedia.org/wiki/Gaussian_elimination
.. _Gauss-Elimination: https://en.wikipedia.org/wiki/Gaussian_elimination
.. _LU Decomposition: https://en.wikipedia.org/wiki/LU_decomposition
.. _sagitta: https://en.wikipedia.org/wiki/Sagitta_(geometry)
.. _math utilities:

.. module:: ezdxf.math

Utility functions and classes located in module :mod:`ezdxf.math`.

Functions
=========

.. autofunction:: is_close_points

.. autofunction:: closest_point

.. autofunction:: convex_hull

.. autofunction:: bspline_control_frame

.. autofunction:: xround

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

    .. automethod:: to_wcs

    .. automethod:: points_to_wcs

    .. automethod:: to_ocs

    .. automethod:: points_to_ocs

    .. automethod:: to_ocs_angle_deg

    .. automethod:: to_ocs_angle_rad

    .. automethod:: from_wcs

    .. automethod:: points_from_wcs

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

    .. automethod:: generate(items: Iterable[Sequence[float]]) -> Iterable[Vector]

    .. automethod:: list(items: Iterable[Sequence[float]]) -> List[Vector]

    .. automethod:: from_angle(angle: float, length: float = 1.) -> Vector

    .. automethod:: from_deg_angle(angle: float, length: float = 1.) -> Vector

    .. automethod:: orthogonal(ccw: bool = True) -> Vector

    .. automethod:: lerp(other: Any, factor=.5) -> Vector

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


.. autoclass:: Vec2(v)

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

    .. automethod:: transform_vectors

    .. automethod:: transpose

    .. automethod:: get_transpose() -> Matrix44

    .. automethod:: determinant

    .. automethod:: inverse


Curves
======

BSpline
-------

.. autoclass:: BSpline
    :members:

BSplineU
--------

.. autoclass:: BSplineU
    :members:

BSplineClosed
-------------

.. autoclass:: BSplineClosed
    :members:


DBSpline
--------

.. autoclass:: DBSpline
    :members:

DBSplineU
---------

.. autoclass:: DBSplineU
    :members:

DBSplineClosed
--------------

.. autoclass:: DBSplineClosed
    :members:

EulerSpiral
-----------

.. autoclass:: EulerSpiral
    :members:

Construction Tools
==================

BoundingBox
-----------

.. autoclass:: BoundingBox
    :members:

BoundingBox2d
-------------

.. autoclass:: BoundingBox2d
    :members:

ConstructionRay
---------------

.. autoclass:: ConstructionRay
    :members:

ConstructionLine
----------------

.. autoclass:: ConstructionLine
    :members:

ConstructionCircle
------------------

.. autoclass:: ConstructionCircle
    :members:

ConstructionArc
---------------

.. autoclass:: ConstructionArc
    :members:

ConstructionBox
---------------

.. autoclass:: ConstructionBox
    :members:


.. _Curve Global Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
.. _clamped curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve.html
.. _open curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-open.html
.. _closed curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
.. _basis: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-basis.html

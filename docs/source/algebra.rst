.. _algebra utilities:

.. module:: ezdxf.algebra

This utilities located in module :mod:`ezdxf.algebra`::

    from ezdxf.algebra import Vector


Functions
---------

.. function:: is_close(a, b)

    Returns True if value is close to value b, uses :code:`math.isclose(a, b, abs_tol=1e-9)` for Python 3, and emulates
    this function for Python 2.7.

.. function:: is_close_points(p1, p2)

    Returns True if all axis of p1 and p2 are close.

.. function:: bspline_control_frame(fit_points, degree=3, method='distance', power=.5)

    Generates the control points for the  B-spline control frame by `Curve Global Interpolation`_.
    Given are the fit points and the degree of the B-spline. The function provides 3 methods for generating the
    parameter vector t:

    1. method = ``uniform``, creates a uniform t vector, form 0 to 1 evenly spaced; see `uniform`_ method
    2. method = ``distance``, creates a t vector with values proportional to the fit point distances, see `chord length`_ method
    3. method = ``centripetal``, creates a t vector with values proportional to the fit point distances^power; see `centripetal`_ method


    :param fit_points: fit points of B-spline, as list of (x, y[, z]) tuples
    :param degree: degree of B-spline
    :param method: calculation method for parameter vector t
    :param power: power for centripetal method

    :returns: a :class:`BSpline` object, with :attr:`BSpline.control_points` containing the calculated control points,
              also :meth:`BSpline.knot_values` returns the used `knot`_ values.

OCS Class
---------

.. class:: OCS

.. method:: OCS.__init__(extrusion=(0, 0, 1))

    Establish an Object Coordinate System for a given extrusion vector.

.. method:: OCS.ocs_to_wcs(point)

    Calculate world coordinates for point in object coordinates.

.. method:: OCS.wcs_to_ocs(point)

    Calculate object coordinates for point in world coordinates.

.. seealso::

    :ref:`ocs`

UCS Class
---------

.. class:: UCS

.. method:: UCS.__init__(origin=(0, 0, 0), ux=(1, 0, 0), uy=(0, 1, 0)

    Establish an User Coordinate System. The UCS is defined by the origin and two unit vectors for the x- and y-axis
    all in WCS, the z-axis is the cross product of ux and uy. Normalization of unit vectors is not required.

    :param origin: defines the UCS origin in world coordinates
    :param ux: defines the UCS x-axis as vector in WCS
    :param uy: defines the UCS y-axis as vector in WCS

.. method:: UCS.ucs_to_wcs(point)

    Calculate world coordinates for point in UCS coordinates.

.. method:: UCS.wcs_to_ucs(point)

    Calculate UCS coordinates for point in world coordinates.

.. seealso::

    :ref:`ucs`


Bulge Related Functions
-----------------------


.. function:: bulge_center(start_point, end_point, bulge)

    Calculate center of arc described by the given bulge parameters.

    :param start_point: start point as (x, y) tuple
    :param end_point: end point as (x, y) tuple
    :param bulge: bulge value as float

    :return: arc center as :class:`Vector`

.. function:: bulge_radius(start_point, end_point, bulge)

    Calculate radius of arc defined by the given bulge parameters.

    :param start_point: start point as (x, y) tuple
    :param end_point: end point as (x, y) tuple
    :param bulge: bulge value as float

    :return: arc radius as float

.. function:: arc_to_bulge(center, start_angle, end_angle, radius)

    Calculate bulge parameters from arc parameters.

    :param center: circle center point as (x, y) tuple
    :param start_angle: start angle in radians
    :param end_angle: end angle in radians
    :param radius: circle radius

    :return: (start_point, end_point, bulge)

.. function:: bulge_to_arc(start_point, end_point, bulge)

    Calculate arc parameters from bulge parameters.

    :param start_point: start point as (x, y) tuple
    :param end_point: end point as (x, y) tuple
    :param bulge: bulge value as float

    :return: (center, start_angle, end_angle, radius)

.. function:: bulge_3_points(start_point, end_point, point)

    Calculate bulge value defined by three points.

    :param start_point: start point of arc
    :param end_point: end point of arc
    :param point: arbitrary point on arc

    :return: bulge value as float

Vector
------

.. class:: Vector

    This is an immutable universal 3d vector object. This class is optimized for universality not for speed.
    Immutable means you can't change (x, y, z) components after initialization::

        v1 = Vector(1, 2, 3)
        v2 = v1
        v2.z = 7  # this is not possible, raises AttributeError
        v2 = Vector(v2.x, v2.y, 7)  # this creates a new Vector() object
        assert v1.z == 3  # and v1 remains unchanged


    Vector initialization:

    - Vector(), returns Vector(0, 0, 0)

    - Vector((x, y)), returns Vector(x, y, 0)

    - Vector((x, y, z)), returns Vector(x, y, z)

    - Vecotr(x, y), returns Vector(x, y, 0)

    - Vector(x, y, z), returns  Vector(x, y, z)

    Addition, subtraction, scalar multiplication and scalar division left and right handed are supported::

        v = Vector(1, 2, 3)
        v + (1, 2, 3) == Vector(2, 4, 6)
        (1, 2, 3) + v == Vector(2, 4, 6)
        v - (1, 2, 3) == Vector(0, 0, 0)
        (1, 2, 3) - v == Vector(0, 0, 0)
        v * 3 == Vector(3, 6, 9)
        3 * v == Vector(3, 6, 9)
        Vector(3, 6, 9) / 3 == Vector(1, 2, 3)
        -Vector(1, 2, 3) == (-1, -2, -3)

    Comparision between vectors and vectors to tuples is supported::

        Vector(1, 2, 3) < Vector (2, 2, 2)
        (1, 2, 3) < tuple(Vector(2, 2, 2))  # conversion necessary
        Vector(1, 2, 3) == (1, 2, 3)

        bool(Vector(1, 2, 3)) is True
        bool(Vector(0, 0, 0)) is False



Vector Attributes
~~~~~~~~~~~~~~~~~

.. attribute:: Vector.x

.. attribute:: Vector.y

.. attribute:: Vector.z

.. attribute:: Vector.xy

    Returns Vector (x, y, 0)

.. attribute:: Vector.tup2

    Returns (x, y) tuple

.. attribute:: Vector.tup3

    Returns (x, y, z) tuple

.. attribute:: Vector.magnitude

    Returns length of vector

.. attribute:: Vector.magnitude_square

    Returns square length of vector

.. attribute:: Vector.is_null

    Returns True for Vector(0, 0, 0) else False

.. attribute:: Vector.spatial_angle_rad

    Returns spatial angle between vector and x-axis in radians

.. attribute:: Vector.spatial_angle_deg

    Returns spatial angle between vector and x-axis in degrees

.. attribute:: Vector.angle_rad

    Returns angle of vector in the xy-plane in radians.

.. attribute:: Vector.angle_deg

    Returns angle of vector in the xy-plane in degrees.

Vector Methods
~~~~~~~~~~~~~~

.. method:: Vector.generate(items)

    Static method returns generator of Vector() objects created from items.

.. method:: Vector.list(items)

    Static method returns list of Vector() objects created from items.

.. method:: Vector.from_rad_angle(angle, length=1.)

    Static method returns Vector() from angle scaled by length, angle in radians.

.. method:: Vector.from_deg_angle(angle, length=1.)

    Static method returns Vector() from angle scaled by length, angle in degree.

.. method:: Vector.__str__()

    Return ``(x, y, z)`` as string.

.. method:: Vector.__repr__()

    Return ``Vector(x, y, z)`` as string.

.. method:: Vector.__len__()

    Returns always 3

.. method:: Vector.__hash__()

.. method:: Vector.copy()

    Returns copy of vector.

.. method:: Vector.__copy__()

    Support for copy.copy().

.. method:: Vector.__deepcopy__(memodict)

    Support for copy.deepcopy().

.. method:: Vector.__getitem__(index)

    Support for indexing :code:`v[0] == v.x; v[1] == v.y; v[2] == v.z;`

.. method:: Vector.__iter__()

    Support for the Python iterator protocol.

.. method:: Vector.__abs__()

    Returns length (magnitude) of vector.

.. method:: Vector.orthogonal(ccw=True)

    Returns orthogonal 2D vector, z value is unchanged.

    :param ccw: counter clockwise if True else clockwise

.. method:: Vector.lerp(other, factor=.5)

    Linear interpolation between vector and other, returns new Vector() object.

    :param other: target vector/point
    :param factor: interpolation factor (0==self, 1=other, 0.5=mid point)

.. method:: Vector.project(other)

    Project vector other onto self, returns new Vector() object.

.. method:: Vector.normalize(length=1)

    Returns new normalized Vector() object, optional scaled by length.

.. method:: Vector.reversed()

    Returns -vector as new Vector() object

.. method:: Vector.__neg__()

    Returns -vector as new Vector() object

.. method:: Vector.__bool__()

    Returns True if vector != (0, 0, 0)

.. method:: Vector.__eq__(other)

.. method:: Vector.__lt__(other)

.. method:: Vector.__add__(other)

.. method:: Vector.__radd__(other)

.. method:: Vector.__sub__(other)

.. method:: Vector.__rsub__(other)

.. method:: Vector.__mul__(other)

.. method:: Vector.__rmul__(other)

.. method:: Vector.__truediv__(other)

.. method:: Vector.__div__(other)

.. method:: Vector.__rtruediv__(other)

.. method:: Vector.__rdiv__(other)

.. method:: Vector.dot(other)

    Returns 'dot' product of vector . other.

.. method:: Vector.cross(other)

    Returns 'cross' product of vector x other

.. method:: Vector.distance(other)

    Returns distance between vector and other.

.. method:: Vector.angle_between(other)

    Returns angle between vector and other in th xy-plane in radians. +angle is counter clockwise orientation.

.. method:: Vector.rot_z_rad(angle)

    Return rotated vector around z axis, angle in radians.

.. method:: Vector.rot_z_deg(angle)

    Return rotated vector around z axis, angle in degrees.


Matrix44
--------

.. class:: Matrix44

    This is a pure Python implementation for 4x4 transformation matrices, to avoid dependency to big numerical packages
    like numpy, and before binary wheels, installation of these packages wasn't always easy on Windows.

    Matrix44 initialization:

    - Matrix44() is the identity matrix.
    - Matrix44(values) values is an iterable with the 16 components of the matrix.
    - Matrix44(row1, row2, row3, row4) four rows, each row with four values.


.. method:: Matrix44.set(*args)

    Reset matrix values:

    - set() creates the identity matrix.
    - set(values) values is an iterable with the 16 components of the matrix.
    - set(row1, row2, row3, row4) four rows, each row with four values.

.. method:: Matrix44.__repr__()

    Returns the representation string of the matrix:

    ``Matrix44((col0, col1, col2, col3), (...), (...), (...))``

.. method:: Matrix44.get_row(row)

    Get row as list of of four float values.

.. method:: Matrix44.set_row(row, values)

    Sets the values in a row.

    :param row: row index [0..3]
    :param values: four column values as iterable.


.. method:: Matrix44.get_col(col)

    Get column as list of of four float values.

.. method:: Matrix44.set_col(col, values)

    Sets the values in a column.

    :param col: column index [0..3]
    :param values: four column values as iterable.

.. method:: Matrix44.copy()

.. method:: Matrix44.__copy__()

.. method:: Matrix44.scale(sx, sy=None, sz=None)

    Class method returns a scaling transformation matrix. If sy is None, sy = sx, and if sz is None sz = sx.

.. method:: Matrix44.translate(x, y, z)

    Class method returns a translation matrix to (x, y, z).

.. method:: Matrix44.x_rotate(angle)

    Class method returns a rotation matrix about the x-axis.

    :param angle: rotation angle in radians

.. method:: Matrix44.y_rotate(angle)

    Class method returns a rotation matrix about the y-axis.

    :param angle: rotation angle in radians

.. method:: Matrix44.z_rotate(angle)

    Class method returns a rotation matrix about the z-axis.

:param angle: rotation angle in radians

.. method:: Matrix44.axis_rotate(axis, angle)

    Class method returns a rotation matrix about an arbitrary axis.

    :param axis: rotation axis as (x, y, z) tuple
    :param angle: rotation angle in radians

.. method:: Matrix44.xyz_rotate(angle_x, angle_y, angle_z)

    Class method returns a rotation matrix for rotation about each axis.

    :param angle_x: rotation angle about x-axis in radians
    :param angle_y: rotation angle about y-axis in radians
    :param angle_z: rotation angle about z-axis in radians


.. method:: Matrix44.perspective_projection(left, right, top, bottom, near, far)

    Class method returns a matrix for a 2d projection.


    :param left: Coordinate of left of screen
    :param right: Coordinate of right of screen
    :param top: Coordinate of the top of the screen
    :param bottom: Coordinate of the bottom of the screen
    :param near: Coordinate of the near clipping plane
    :param far: Coordinate of the far clipping plane


.. method:: Matrix44.perspective_projection_fov(fov, aspect, near, far)

    Class method returns a matrix for a 2d projection.


    :param fov: The field of view (in radians)
    :param aspect: The aspect ratio of the screen (width / height)
    :param near: Coordinate of the near clipping plane
    :param far: Coordinate of the far clipping plane

.. method:: Matrix44.chain(*matrices)

    Compose a transformation matrix from one or more matrices.

.. method:: Matrix44.__setitem__(coord, value)

    Set (row, column) element.

.. method:: Matrix44.__getitem__(coord)

    Get (row, column) element.

.. method:: Matrix44.__iter__()

    Iterates over all matrix values.

.. method:: Matrix44.__mul__(other)

    Returns a new matrix as result of the matrix multiplication with another matrix.

.. method:: Matrix44.__imul__(other)

    Inplace multiplication with another matrix.

.. method:: Matrix44.fast_mul(other)

    Multiplies this matrix with other matrix inplace.

    Assumes that both matrices have a right column of (0, 0, 0, 1). This is True for matrices composed of
    rotations,  translations and scales. fast_mul is approximately 25% quicker than __imul__().

.. method:: Matrix44.rows()

    Iterate over rows as 4-tuples.

.. method:: Matrix44.columns()

    Iterate over columns as 4-tuples.

.. method:: Matrix44.transform(vector)

    Transforms a 3d vector and return the result as a tuple.

.. method:: Matrix44.transform_vectors(vectors)

    Returns a list of transformed vectors.

.. method:: Matrix44.transpose()

    Swaps the rows for columns inplace.

.. method:: Matrix44.get_transpose()

    Returns a new transposed matrix.

.. method:: Matrix44.determinant()

    Returns determinant.

.. method:: Matrix44.inverse()

    Returns the inverse of the matrix.

    :raises ZeroDivisionError: if matrix has no inverse.

BSpline
-------

.. class:: BSpline

    Calculate the vertices of a B-spline curve, using an uniform open `knot`_ vector (`clamped curve`_).

.. attribute:: BSpline.control_points

    Control points as list of :class:`Vector` objects

.. attribute:: BSpline.count

    Count of control points, (n + 1 in math definition).

.. attribute:: BSpline.order

    Order of B-spline = degree +  1

.. attribute:: BSpline.degree

    Degree (p) of B-spline = order - 1

.. attribute:: BSpline.max_t

    Max `knot`_ value.

.. method:: BSpline.knot_values()

    Returns a list of `knot`_ values as floats, the knot vector always has order+count values (n + p + 2 in math definition)

.. method:: BSpline.basis_values(t)

    Returns the `basis`_ vector for position t.

.. method:: BSpline.approximate(segments)

    Approximates the whole B-spline from 0 to max_t, by line segments as a list of vertices, vertices count = segments + 1

.. method:: BSpline.point(t)

    Returns the B-spline vertex at position t as (x, y[, z]) tuple.


BSplineU
--------

.. class:: BSpline(BSpline)

    Calculate the points of a B-spline curve, uniform (periodic) `knot`_ vector (`open curve`_).

BSplineClosed
-------------

.. class:: BSplineClosed(BSplineU)

    Calculate the points of a closed uniform B-spline curve (`closed curve`_).


DBSpline
--------

.. class:: DBSpline(BSpline)

    Calculate points and derivative of a B-spline curve, using an uniform open `knot`_ vector (`clamped curve`_).

.. method:: DBSpline.point(t)

    Returns the B-spline vertex, 1. derivative and 2. derivative at position t as tuple (vertex, d1, d2), each value
    is a (x, y, z) tuple.

DBSplineU
---------

.. class:: DBSplineU(DBSpline)

    Calculate points and derivative of a B-spline curve, uniform (periodic) `knot`_ vector (`open curve`_).

DBSplineClosed
--------------

.. class:: DBSplineClosed(DBSplineU)

    Calculate the points and derivative of a closed uniform B-spline curve (`closed curve`_).


.. _Curve Global Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
.. _clamped curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve.html
.. _open curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-open.html
.. _closed curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
.. _basis: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-basis.html

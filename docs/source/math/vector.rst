.. module:: ezdxf.ezmath

This class located in module :mod:`ezdxf.ezmath`::

    from ezdxf.ezmath import Vector


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

    Comparison between vectors and vectors to tuples is supported::

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

.. attribute:: Vector.xyz

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

.. method:: Vector.replace(x=None, y=None, z=None)

    Return new Vector() with replaced components != None.

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

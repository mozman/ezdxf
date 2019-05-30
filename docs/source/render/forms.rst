.. module:: ezdxf.render.forms

Forms
=====

    This module provides functions to create 2D and 3D forms as vertices or mesh objects.

    2D Forms

    - :meth:`circle`
    - :meth:`ellipse`
    - :meth:`euler_spiral`
    - :meth:`ngon`
    - :meth:`star`
    - :meth:`gear`

    3D Forms

    - :meth:`cube`
    - :meth:`cylinder`
    - :meth:`cone`

    3D Form Builder

    - :meth:`extrude`
    - :meth:`from_profiles_linear`
    - :meth:`from_profiles_spline`
    - :meth:`rotation_form`

2D Forms
--------

    Basic 2D shapes as iterable of :class:`~ezdxf.math.Vector`.


.. function:: circle(count, radius=1, elevation=0, close=False)

    Create polygon vertices for a circle with *radius* and *count* vertices.

    :param count: count of polygon vertices
    :param radius: circle radius
    :param elevation: z axis for all vertices
    :param close: yields first vertex also as last vertex if True.
    :returns: yields :class:`~ezdxf.math.Vector` objects in counter clockwise orientation

.. function:: ellipse(count, rx=1, ry=1, start_param=0, end_param=2*pi, elevation=0)

    Create polygon vertices for an ellipse with *rx* as x-axis radius and *ry* for y-axis radius with *count* vertices.
    The curve goes from *start_param* to *end_param* in counter clockwise orientation.

    :param count: count of polygon vertices
    :param rx: ellipse x-axis radius
    :param ry: ellipse y-axis radius
    :param start_param: start of ellipse in range 0 ... 2\*pi
    :param end_param: end of ellipse in range 0 ... 2\*pi
    :param elevation: z axis for all vertices
    :returns: yields :class:`~ezdxf.math.Vector` objects

.. function:: euler_spiral(count, length=1, curvature=1, elevation=0)

    Create polygon vertices for an euler spiral of a given *length* and
    radius of *curvature*. This is a parametric curve, which always starts
    at the origin.

    :param count: count of polygon vertices
    :param length: length of curve in drawing units
    :param curvature: radius of curvature
    :param elevation: z-axis for all vertices
    :returns: yields :class:`~ezdxf.math.Vector` objects

.. function:: ngon(count, length=None, radius=0, rotation=0, elevation=0, close=False)

    Returns the corners of a regular polygon as iterable of :class:`~ezdxf.math.Vector` (z=`elevation`). The polygon
    size is determined by the edge `length` or the circum `radius` argument. If both are given `length` will be taken.

    :param count: count of polygon corners >= 3
    :param length: length of polygon side
    :param radius: circum radius
    :param rotation: rotation angle in radians
    :param elevation: z axis for all vertices
    :param close: yields first vertex also as last vertex if True.
    :returns: yields :class:`~ezdxf.math.Vector` objects

.. function:: star(count, r1, r2, rotation=0, elevation=0, close=False)

    Create a star shape as iterable of :class:`~ezdxf.math.Vector` (z=`elevation`).

    Argument `count` defines the count of star spikes, `r1` defines the radius of the "outer" vertices and `r2`
    defines the radius of the "inner" vertices, but this does not mean that `r1` has to greater than `r2`.

    :param count: spike count >= 3
    :param r1: radius 1
    :param r2: radius 2
    :param rotation: rotation angle in radians
    :param elevation: z axis for all vertices
    :param close: yields first vertex also as last vertex if True.
    :returns: yields :class:`~ezdxf.math.Vector` objects

.. function:: gear(count, top_width, bottom_width, height, outside_radius, close=False)

    Create gear (cogwheel) vertices as iterable of :class:`~ezdxf.math.Vector` (z=`elevation`)

    Warning: this function does not create mechanical correct gears!

    see also: https://en.wikipedia.org/wiki/Gear

    :param count: teeth count >= 3
    :param top_width: teeth width at outside radius
    :param bottom_width: teeth width at base radius
    :param height: teeth height; base radius = outside radius - height
    :param outside_radius: outside radius
    :param elevation: z axis for all vertices
    :param close: yields first vertex also as last vertex if True.
    :returns: yields :class:`~ezdxf.math.Vector` objects

3D Forms
--------

Create 3D forms as :class:`~ezdxf.render.MeshBuilder` or :class:`~ezdxf.render.MeshVertexMerger`.


.. function:: cube(center=True, matrix=None)

    Create a cube.

    :param matrix: transformation matrix as :class:`~ezdxf.math.Matrix44`
    :param center: 'mass' center of cube in (0, 0, 0) if True, else first corner at (0, 0, 0)
    :returns: :class:`~ezdxf.render.MeshBuilder`

.. function:: cylinder(count, radius=1., top_radius=None, top_center=(0, 0, 1), caps=True)

    Create a cylinder.

    :param count: profiles edge count
    :param radius: radius for bottom profile
    :param top_radius: radius for top profile, same as radius if top_radius is None
    :param top_center: location vector for the center of the top profile
    :param caps: close hull with bottom cap and top cap (as N-gons)
    :returns: :class:`~ezdxf.render.MeshVertexMerger`

.. function:: cone(count, radius, apex=(0, 0, 1), caps=True)

    Create a cone.

    :param count: edge count of basis
    :param radius: radius of basis
    :param apex: apex of the cone
    :param caps: add a bottom face if true
    :returns: :class:`~ezdxf.render.MeshVertexMerger`

3D Form Builder
---------------

.. function:: extrude(profile, path, close=True)

    Extrude a profile polygon along a path polyline, vertices of profile should be in counter clockwise order.

    :param profile: sweeping profile as list of (x, y, z) tuples in counter clock wise order
    :param path:  extrusion path as list of (x, y, z) tuples
    :param close: close profile polygon if True

    :returns: :class:`~ezdxf.render.MeshVertexMerger`

.. function:: from_profiles_linear(profiles, close=True, caps=False)

    Mesh by linear connected profiles.

    :param profiles: list of profiles
    :param close: close profile polygon if True
    :param caps: close hull with bottom cap and top cap (as N-gons)
    :returns: :class:`~ezdxf.render.MeshVertexMerger`

.. function:: from_profiles_spline(profiles, subdivide=4, close=True, caps=False)

    Mesh entity by spline interpolation between given profiles. Requires at least 4 profiles.
    A subdivide value of 4, means, create 4 face loops between two profiles, without interpolation
    two profiles create one face loop.


    :param profiles: list of profiles
    :param subdivide: count of face loops
    :param close: close profile polygon if True
    :param caps: close hull with bottom cap and top cap (as N-gons)
    :returns: :class:`~ezdxf.render.MeshVertexMerger`

.. function:: rotation_form(count, profile, angle=2*pi, axis=(1, 0, 0))

    Mesh by rotating a profile around an axis.

    :param count: count of rotated profiles
    :param profile: profile to rotate as list of vertices
    :param angle: rotation angle in radians
    :param axis: rotation axis
    :returns: :class:`~ezdxf.render.MeshVertexMerger`

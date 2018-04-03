.. module:: ezdxf.addons

Forms
=====

Basic Forms
-----------

.. function:: circle(count, radius=1.0, z=0., close=False)

    Create polygon vertices for a circle with *radius* and *count* corners at *z* height.

    :param count: polygon corners
    :param radius: circle radius
    :param z: z axis value
    :param close: yields first vertex also as last vertex if True.
    :returns: yields :class:`~ezdxf.algebra.Vector` objects in count clockwise orientation

.. function:: cube(center=True, matrix=None)

    Create a cube.

    :param matrix: transformation matrix as :class:`~ezdxf.algebra.Matrix44`
    :param center: 'mass' center of cube in (0, 0, 0) if True, else first corner at (0, 0, 0)
    :returns: :class:`~ezdxf.addons.MeshBuilder`

.. function:: cylinder(count, radius=1., top_radius=None, top_center=(0, 0, 1), caps=True)

    Create a cylinder.

    :param count: profiles edge count
    :param radius: radius for bottom profile
    :param top_radius: radius for top profile, if None top_radius == radius
    :param top_center: location vector for the center of the top profile
    :param caps: close hull with bottom cap and top cap (as N-gons)
    :returns: :class:`~ezdxf.addons.MeshVertexMerger`

.. function:: cone(count, radius, apex=(0, 0, 1), caps=True)

    Create a cone.

    :param count: edge count of basis
    :param radius: radius of basis
    :param apex: apex of the cone
    :param caps: add a bottom face if true
    :returns: :class:`~ezdxf.addons.MeshVertexMerger`

Form Builder
------------

.. function:: extrude(profile, path, close=True)

    Extrude a profile polygon along a path polyline, vertices of profile should be in counter clockwise order.

    :param profile: sweeping profile as list of (x, y, z) tuples in counter clock wise order
    :param path:  extrusion path as list of (x, y, z) tuples
    :param close: close profile polygon if True

    :returns: :class:`~ezdxf.addons.MeshVertexMerger`

.. function:: from_profiles_linear(profiles, close=True, caps=False)

    Mesh by linear connected profiles.

    :param profiles: list of profiles
    :param close: close profile polygon if True
    :param caps: close hull with bottom cap and top cap (as N-gons)
    :returns: :class:`~ezdxf.addons.MeshVertexMerger`

.. function:: from_profiles_spline(profiles, subdivide=4, close=True, caps=False)

    Mesh entity by spline interpolation between given profiles. Requires at least 4 profiles.
    A subdivide value of 4, means, create 4 face loops between two profiles, without interpolation
    two profiles create one face loop.


    :param profiles: list of profiles
    :param subdivide: count of face loops
    :param close: close profile polygon if True
    :param caps: close hull with bottom cap and top cap (as N-gons)
    :returns: :class:`~ezdxf.addons.MeshVertexMerger`

.. function:: rotation_form(count, profile, angle=2*pi, axis=(1, 0, 0))

    Mesh by rotating a profile around an axis.

    :param count: count of rotated profiles
    :param profile: profile to rotate as list of vertices
    :param angle: rotation angle in radians
    :param axis: rotation axis
    :returns: :class:`~ezdxf.addons.MeshVertexMerger`

.. class:: MengerSponge

.. class:: SierpinskyPyramid

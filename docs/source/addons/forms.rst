.. module:: ezdxf.addons

Forms
=====

Basic Forms
-----------

.. function:: circle(count, radius=1, elevation=0, close=False)

    Create polygon vertices for a circle with *radius* and *count* vertices.

    :param count: count of polygon vertices
    :param radius: circle radius
    :param elevation: z axis for all vertices
    :param close: yields first vertex also as last vertex if True.
    :returns: yields :class:`~ezdxf.algebra.Vector` objects in counter clockwise orientation

.. function:: ellipse(count, rx=1, ry=1, start_param=0, end_param=2*pi, elevation=0)

    Create polygon vertices for an ellipse with *rx* as x-axis radius and *ry* for y-axis radius with *count* vertices.
    The curve goes from *start_param* to *end_param* in counter clockwise orientation.

    :param count: count of polygon vertices
    :param rx: ellipse x-axis radius
    :param ry: ellipse y-axis radius
    :param start_param: start of ellipse in range 0 ... 2\*pi
    :param end_param: end of ellipse in range 0 ... 2\*pi
    :param elevation: z axis for all vertices
    :returns: yields :class:`~ezdxf.algebra.Vector` objects

.. function:: euler_spiral(count, length=1, curvature=1, elevation=0)

    Create polygon vertices for an euler spiral of a given *length* and
    radius of *curvature*. This is a parametric curve, which always starts
    at the origin.

    :param count: count of polygon vertices
    :param length: length of curve in drawing units
    :param curvature: radius of curvature
    :param elevation: z-axis for all vertices
    :returns: yields :class:`~ezdxf.algebra.Vector` objects

.. function:: cube(center=True, matrix=None)

    Create a cube.

    :param matrix: transformation matrix as :class:`~ezdxf.algebra.Matrix44`
    :param center: 'mass' center of cube in (0, 0, 0) if True, else first corner at (0, 0, 0)
    :returns: :class:`~ezdxf.addons.MeshBuilder`

.. function:: cylinder(count, radius=1., top_radius=None, top_center=(0, 0, 1), caps=True)

    Create a cylinder.

    :param count: profiles edge count
    :param radius: radius for bottom profile
    :param top_radius: radius for top profile, same as radius if top_radius is None
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

MengerSponge
------------

Build a 3D `Menger sponge <https://en.wikipedia.org/wiki/Menger_sponge>`_.

.. class:: MengerSponge

.. method:: MengerSponge.__init__(location=(0, 0, 0), length=1., level=1, kind=0)

    :param location: location of lower left corner as (x, y, z) tuple
    :param length: side length
    :param level: subdivide level
    :param kind: type of menger sponge:

         - 0 = original menger sponge
         - 1 = Variant XOX
         - 2 = Variant OXO
         - 3 = Jerusalem Cube

.. method:: MengerSponge.render(layout, merge=False, dxfattribs=None, matrix=None)

    Renders the menger sponge into layout, set merge == *True* for rendering the whole menger sponge into one
    :class:`Mesh` entity, set merge to *False* for rendering the individual cubes of the menger sponge as
    :class:`Mesh` entities.

    :param layout: ezdxf :class:`Layout` object
    :param merge: *True* for one :class:`Mesh` entity, *False* for individual :class:`Mesh` entities per cube
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}
    :param matrix: transformation matrix as :class:`~ezdxf.algebra.Matrix44`

.. method:: MengerSponge.cubes()

    Generates all cubes of the menger sponge as individual :class:`~ezdxf.addons.MeshBuilder` objects.

.. method:: MengerSponge.mesh()

    Returns geometry as one :class:`~ezdxf.addons.MeshVertexMerger` entity.

SierpinskyPyramid
-----------------

Build a 3D `Sierpinsky Pyramid <https://en.wikipedia.org/wiki/Sierpinski_triangle>`_.

.. class:: SierpinskyPyramid

.. method:: SierpinskyPyramid.__init__(location=(0, 0, 0), length=1., level=1, sides=4)

    :param location: location of base center as (x, y, z) tuple
    :param length: side length
    :param level: subdivide level
    :param sides: sides of base geometry

.. method:: SierpinskyPyramid.render(layout, merge=False, dxfattribs=None, matrix=None)

    Renders the sierpinsky pyramid into layout, set merge == *True* for rendering the whole sierpinsky pyramid into one
    :class:`Mesh` entity, set merge to *False* for rendering the individual pyramids of the sierpinsky pyramid as
    :class:`Mesh` entities.

    :param layout: ezdxf :class:`Layout` object
    :param merge: *True* for one :class:`Mesh` entity, *False* for individual :class:`Mesh` entities per cube
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}
    :param matrix: transformation matrix as :class:`~ezdxf.algebra.Matrix44`

.. method:: SierpinskyPyramid.pyramids()

    Generates all pyramids of the sierpinsky pyramid as individual :class:`~ezdxf.addons.MeshBuilder` objects.

.. method:: SierpinskyPyramid.mesh()

    Returns geometry as one :class:`~ezdxf.addons.MeshVertexMerger` entity.
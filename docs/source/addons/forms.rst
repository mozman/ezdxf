.. module:: ezdxf.addons

Showcase Forms
==============

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
    :param matrix: transformation matrix as :class:`~ezdxf.math.Matrix44`

.. method:: MengerSponge.cubes()

    Generates all cubes of the menger sponge as individual :class:`~ezdxf.render.MeshBuilder` objects.

.. method:: MengerSponge.mesh()

    Returns geometry as one :class:`~ezdxf.render.MeshVertexMerger` entity.

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
    :param matrix: transformation matrix as :class:`~ezdxf.math.Matrix44`

.. method:: SierpinskyPyramid.pyramids()

    Generates all pyramids of the sierpinsky pyramid as individual :class:`~ezdxf.render.MeshBuilder` objects.

.. method:: SierpinskyPyramid.mesh()

    Returns geometry as one :class:`~ezdxf.render.MeshVertexMerger` entity.
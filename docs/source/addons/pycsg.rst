.. automodule:: ezdxf.addons.pycsg

PyCSG
=====

Constructive Solid Geometry (CSG) is a modeling technique that uses Boolean
operations like union and intersection to combine 3D solids. This library
implements CSG operations on meshes elegantly and concisely using BSP trees,
and is meant to serve as an easily understandable implementation of the
algorithm. All edge cases involving overlapping coplanar polygons in both
solids are correctly handled.

.. versionadded:: 0.11

Example for usage:

.. code-block:: Python

    import ezdxf
    from ezdxf.render.forms import cube, cylinder_2p
    from ezdxf.addons.pycsg import CSG

    # create new DXF document
    doc = ezdxf.new()
    msp = doc.modelspace()

    # create same geometric primitives as MeshTransformer() objects
    cube1 = cube()
    cylinder1 = cylinder_2p(count=32, base_center=(0, -1, 0), top_center=(0, 1, 0), radius=.25)

    # build solid union
    union = CSG(cube1) + CSG(cylinder1)
    # convert to mesh and render mesh to modelspace
    union.mesh().render(msp, dxfattribs={'color': 1})

    # build solid difference
    difference = CSG(cube1) - CSG(cylinder1)
    # convert to mesh, translate mesh and render mesh to modelspace
    difference.mesh().translate(1.5).render(msp, dxfattribs={'color': 3})

    # build solid intersection
    intersection = CSG(cube1) * CSG(cylinder1)
    # convert to mesh, translate mesh and render mesh to modelspace
    intersection.mesh().translate(2.75).render(msp, dxfattribs={'color': 5})

    doc.saveas('csg.dxf')

.. image:: gfx/pycsg01.png

This CSG kernel supports only meshes as :class:`~ezdxf.render.MeshBuilder` objects, which can be created from and
converted to DXF :class:`~ezdxf.entities.Mesh` entities.

This CSG kernel is **not** compatible with ACIS objects like :class:`~ezdxf.entities.Solid3d`,
:class:`~ezdxf.entities.Body`, :class:`~ezdxf.entities.Surface` or :class:`~ezdxf.entities.Region`.

.. note::

    This is a pure Python implementation, don't expect great performance and the implementation is based on an
    unbalanced `BSP tree`_, so in the case of :class:`RecursionError`, increase the recursion limit:

    .. code-block:: Python

         import sys

         actual_limit = sys.getrecursionlimit()
         # default is 1000, increasing too much may cause a seg fault
         sys.setrecursionlimit(10000)

         ...  # do the CSG stuff

         sys.setrecursionlimit(actual_limit)

CSG Class
---------

.. autoclass:: CSG(mesh: MeshBuilder = None)

    .. automethod:: mesh() -> MeshTransformer

    .. automethod:: union(other: CSG) -> CSG

    .. method:: __add__(other: CSG) -> CSG

       .. code-block:: Python

            union = A + B

    .. automethod:: subtract(other: CSG) -> CSG

    .. method:: __sub__(other: CSG) -> CSG

       .. code-block:: Python

            difference = A - B

    .. automethod:: intersect(other: CSG) -> CSG

    .. method:: __mul__(other: CSG) -> CSG

       .. code-block:: Python

            intersection = A * B

    .. automethod:: inverse() -> CSG

License
-------

- Original implementation `csg.js`_, Copyright (c) 2011 Evan Wallace (http://madebyevan.com/), under the MIT license.
- Python port `pycsg`_, Copyright (c) 2012 Tim Knip (http://www.floorplanner.com), under the MIT license.
- Additions by Alex Pletzer (Pennsylvania State University)
- Integration as `ezdxf` add-on, Copyright (c) 2020, Manfred Moitzi, MIT License.

.. _csg.js: https://github.com/evanw/csg.js
.. _pycsg: https://github.com/timknip/pycsg
.. _BSP tree: https://en.wikipedia.org/wiki/Binary_space_partitioning
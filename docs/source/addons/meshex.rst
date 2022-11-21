.. module:: ezdxf.addons.meshex

.. _meshex:

MeshExchange
============

The :mod:`ezdxf.addons.meshex` module provides functions to exchange meshes
with other tools in the following file formats:

    - `STL`_: import/export, supports only triangles as faces
    - `OFF`_: import/export, supports ngons as faces and is more compact than STL
    - `OBJ`_: import/export, supports ngons as faces and can contain multiple
      meshes in one file
    - `PLY`_: export only, supports ngons as faces
    - `OpenSCAD`_: export as `polyhedron`_, supports ngons as faces
    - `IFC4`_: export only, supports ngons as faces

The source or target object is always a :class:`~ezdxf.render.MeshBuilder`
instance and therefore the supported features are also limited by this class.
Only vertices and faces are exchanged, colors, textures and explicit face- and
vertex normals are lost.

.. note::

    This add-on is not a replacement for a proper file format
    interface for this data formats! It's just a simple way to
    exchange meshes with other tools like `OpenSCAD`_ or `MeshLab`_.

.. warning::

    The meshes created by the :mod:`ezdxf.addons.pycsg` add-on are usually not
    suitable for export because they often violate the vertex-to-vertex rule:
    A vertex of a face cannot lie on the edge of another face.
    This was one of the reasons to create this addon to get an interface to
    `OpenSCAD`_.

Example for a simple STL to DXF converter:

.. code-block:: Python

    import sys
    import ezdxf
    from ezdxf.addons import meshex

    try:
        mesh = meshex.stl_readfile("your.stl")
    except (meshex.ParsingError, IOError) as e:
        print(str(e))
        sys.exit(1)

    doc = ezdxf.new()
    mesh.render_mesh(doc.modelspace())
    doc.saveas("your.dxf")

.. seealso::

    Example script `meshex_export.py`_ at github.

Import
------

.. autofunction:: stl_readfile

.. autofunction:: stl_loads

.. autofunction:: stl_loadb

.. autofunction:: off_readfile

.. autofunction:: off_loads

.. autofunction:: obj_readfile

.. autofunction:: obj_loads

Export
------

.. autofunction:: stl_dumps

.. autofunction:: stl_dumpb

.. autofunction:: off_dumps

.. autofunction:: obj_dumps

.. autofunction:: ply_dumpb

.. autofunction:: scad_dumps

.. autofunction:: ifc4_dumps

.. autofunction:: export_ifcZIP

.. autoclass:: IfcEntityType

    .. attribute::  POLYGON_FACE_SET

        "SurfaceModel" representation usable for open or closed surfaces.

    .. attribute::  CLOSED_SHELL

        "Brep" representation usable for closed surfaces.

    .. attribute::  OPEN_SHELL

        "SurfaceModel" representation usable for open surfaces.

.. _OpenSCAD: https://openscad.org/index.html
.. _MeshLab: https://www.meshlab.net
.. _STL: https://en.wikipedia.org/wiki/STL_(file_format)
.. _OFF: https://en.wikipedia.org/wiki/OFF_(file_format)
.. _OBJ: https://en.wikipedia.org/wiki/OBJ_(file_format)
.. _PLY: https://en.wikipedia.org/wiki/PLY_(file_format)
.. _polyhedron: https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Primitive_Solids#polyhedron
.. _IFC4: https://en.wikipedia.org/wiki/Industry_Foundation_Classes
.. _meshex_export.py: https://github.com/mozman/ezdxf/blob/master/examples/addons/meshex_export.py
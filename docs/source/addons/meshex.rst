.. module:: ezdxf.addons.meshex

.. _meshex:

MeshExchange
============

.. versionadded:: 0.18

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
Only vertices and faces are exchanged, colors, textures and normals are lost.

.. note::

    This add-on is not a replacement for a proper file format
    interface for this data formats! It's just a simple way to
    exchange meshes with other tools like `OpenSCAD`_ or `MeshLab`_.

.. warning::

    The meshes created with the addon :mod:`ezdxf.addons.pycsg` are usually not
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

Import
------

.. autofunction:: stl_readfile(filename: Union[str, os.PathLike]) -> MeshTransformer

.. autofunction:: stl_loads(content: str) -> MeshTransformer

.. autofunction:: stl_loadb(buffer: bytes) -> MeshTransformer

.. autofunction:: off_readfile(filename: Union[str, os.PathLike]) -> MeshTransformer

.. autofunction:: off_loads(content: str) -> MeshTransformer

.. autofunction:: obj_readfile(filename: Union[str, os.PathLike]) -> List[MeshTransformer]

.. autofunction:: obj_loads(content: str) -> List[MeshTransformer]

Export
------

.. autofunction:: stl_dumps(mesh: MeshBuilder) -> str

.. autofunction:: stl_dumpb(mesh: MeshBuilder) -> bytes

.. autofunction:: off_dumps(mesh: MeshBuilder) -> str

.. autofunction:: obj_dumps(mesh: MeshBuilder) -> str

.. autofunction:: ply_dumpb(mesh: MeshBuilder) -> bytes

.. autofunction:: scad_dumps(mesh: MeshBuilder) -> str

.. autofunction:: ifc4_dumps(mesh: MeshBuilder, entity_type = IfcEntityType.POLYGON_FACE_SET, layer="MeshExport", color=(1, 1, 1)) -> str

.. autofunction:: export_ifcZIP(filename: Union[str, os.PathLike] , mesh: MeshBuilder, entity_type = IfcEntityType.POLYGON_FACE_SET, layer="MeshExport", color=(1, 1, 1))

.. autoclass:: IfcEntityType

    .. attribute::  POLYGON_FACE_SET

    .. attribute::  CLOSED_SHELL


.. _OpenSCAD: https://openscad.org/index.html
.. _MeshLab: https://www.meshlab.net
.. _STL: https://en.wikipedia.org/wiki/STL_(file_format)
.. _OFF: https://en.wikipedia.org/wiki/OFF_(file_format)
.. _OBJ: https://en.wikipedia.org/wiki/OBJ_(file_format)
.. _PLY: https://en.wikipedia.org/wiki/PLY_(file_format)
.. _polyhedron: https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Primitive_Solids#polyhedron
.. _IFC4: https://en.wikipedia.org/wiki/Industry_Foundation_Classes
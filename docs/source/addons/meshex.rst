.. module:: ezdxf.addons.meshex

.. _meshex:

MeshExchange
============

The :mod:`ezdxf.addons.meshex` module provides functions to exchange meshes
with other file formats like:

    - `STL`_
    - `OFF`_
    - `PLY`_
    - `OBJ`_

The source or target entity is always a :class:`~ezdxf.render.MeshBuilder`
instance and therefore the supported features are also limited by this class.
Only vertices and faces are exchanged, colors, textures and normals are lost.

.. note::

    This add-on is not a replacement for a proper file format
    interfaces for this data formats! It's just a simple and quick way to
    exchange meshes with other tools like `OpenSCAD`_.

.. autofunction:: stl_readfile

.. autofunction:: stl_loads

.. _OpenSCAD: https://openscad.org/index.html
.. _STL: https://en.wikipedia.org/wiki/STL_(file_format)
.. _PLY: https://en.wikipedia.org/wiki/PLY_(file_format)
.. _OFF: https://en.wikipedia.org/wiki/OFF_(file_format)
.. _OBJ: https://en.wikipedia.org/wiki/OBJ_(file_format)

Tag Data Structures
===================

.. module:: ezdxf.lldxf

DXFTag
------

    The :class:`DXFTag` is the basic DXF data type, this data type is per definition immutable (but not per
    implementation for sake of speed)

.. class:: DXFTag

.. attribute:: DXFTag.code

    DXF group code (read only)

.. attribute:: DXFTag.value

    DXF tag value (read only)

.. method:: DXFTag.__str__()

.. method:: DXFTag.__repr__()

.. method:: DXFTag.__getitem__()

.. method:: DXFTag.__iter__()

.. method:: DXFTag.dxfstr()

    Returns the DXF string e.g. '  0\nLINE\n'

.. method:: DXFTag.clone()

    Returns a clone of itself, this method is necessary for the more complex (and not immutable) DXF tag types.

DXFVertex
---------

    Represents a 2D or 3D vertex, stores only the group code of the x-component of the vertex, because the y-group-code
    is x-group-code + 10 and z-group-code id x-group-code+20, this is a rule that ALWAYS applies.

.. class:: DXFVertex(DXFTag)

.. attribute:: DXFVertex.code

    DXF group code for the x-component (read only)

.. attribute:: DXFVertex.value

    x, y[, z] coordinates as :code:`array.array('d')` object (read/write)

.. method:: DXFVertex.__str__()

.. method:: DXFVertex.__repr__()

.. method:: DXFVertex.__getitem__()

.. method:: DXFVertex.__iter__()

.. method:: DXFVertex.dxftags()

    Returns all vertex components as single :class:`DXFTag` objects.

.. method:: DXFVertex.dxfstr()

    Returns the DXF string for all vertex components.

.. method:: DXFVertex.clone()

    Returns a clone of itself.

Tags
----

    A list of DXF tags, inherits from Python standard list.

.. class:: Tags(list)


TODO

ExtendedTags
------------

    Represents the extended DXF tag structure introduced with DXF R13.

.. class:: ExtendedTags

TODO

Packed Tags
===========

    The following tag types store multiple tags in one object to reduce the memory footprint.

TagList
-------

    Stores multiple tags with the same group code in a standard Python list.

.. class:: TagList

TODO

TagArray
--------

    Stores multiple tags with the same group code in a :code:`array.array()` object.

.. class:: TagArray

TODO

TagDict
-------

    Stores multiple key/value tags with the same group code in a standard Python dict.

.. class:: TagDict

TODO


VertexArray
-----------

    Stores multiple vertex tags with the same group code in a :code:`array.array('d')` object.

.. class:: VertexArray

TODO


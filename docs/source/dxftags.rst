Single Tags
===========

.. automodule:: ezdxf.lldxf.types

Functions
---------

.. autofunction:: dxftag

.. autofunction:: tuples_to_tags


Classes
-------

.. autoclass:: DXFTag
    :members: __str__, __repr__, __getitem__, __iter__, __eq__, __hash__, dxfstr, clone


.. autoclass:: DXFBinaryTag(DXFTag)
    :members:

.. autoclass:: DXFVertex(DXFTag)
    :members:


Constants
---------

.. attribute:: NONE_TAG

    Special tag representing a none existing tag.

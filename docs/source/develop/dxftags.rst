.. automodule:: ezdxf.lldxf.types

DXFTag Factory Functions
========================

.. autofunction:: dxftag

.. autofunction:: tuples_to_tags


DXFTag
======

.. autoclass:: DXFTag
    :members: __str__, __repr__, __getitem__, __iter__, __eq__, __hash__, dxfstr, clone

    .. attribute:: code

        group code as int (do not change)

    .. attribute:: value

        tag value (read-only property)

DXFBinaryTag
============

.. autoclass:: DXFBinaryTag(DXFTag)
    :members:

DXFVertex
=========

.. autoclass:: DXFVertex(DXFTag)
    :members:


NONE_TAG
========

.. attribute:: NONE_TAG

    Special tag representing a none existing tag.

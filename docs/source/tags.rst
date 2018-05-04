Tag Data Structures
===================

.. module:: ezdxf.lldxf

Required DXF tag interface:

    - property code: group code as int
    - property value: tag value of unspecific type
    - method dxfstr(): returns the DXF string
    - method clone(): returns a deep copy of tag


DXFTag
------

    The :class:`DXFTag` is the basic DXF data type, this data type is per definition immutable (but not per
    implementation for sake of speed)

.. class:: DXFTag

.. attribute:: DXFTag.code

    DXF group code (read only), interface definition

.. attribute:: DXFTag.value

    DXF tag value (read only)

.. method:: DXFTag.__str__()

.. method:: DXFTag.__repr__()

.. method:: DXFTag.__getitem__()

    Support for indexing.

.. method:: DXFTag.__iter__()

    Support for iterator protocol.

.. method:: DXFTag.dxfstr()

    Returns the DXF string e.g. '  0\nLINE\n'

.. method:: DXFTag.clone()

    Returns a clone of itself, this method is necessary for the more complex (and not immutable) DXF tag types.

DXFBinaryTag
------------

    Represents binary data compact as binary strings. This tag is immutable.

.. class:: DXFBinaryTag(DXFTag)

DXFVertex
---------

    Represents a 2D or 3D vertex, stores only the group code of the x-component of the vertex, because the y-group-code
    is x-group-code + 10 and z-group-code id x-group-code+20, this is a rule that ALWAYS applies. This tag is `mutable`.

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
    Unlike the statement in the DXF Reference "Do not write programs that rely on the order given here",
    tag order is sometimes essential and some group codes may appear multiples times in one entity. At the
    worst case (MATERIAL: normal map shares group codes with diffuse map) using same group codes with different
    meanings.


.. class:: Tags(list)


.. method:: Tags.from_text(text)

    Constructor from DXF string.

.. method:: Tags.strip(tags, codes)

    Constructor from `tags`, strips all tags with group codes in `codes` from `tags`.

    :param codes: iterable of group codes

.. method:: Tags.get_handle()

    Get DXF handle, raises DXFValueError if handle not exists.

.. method:: Tags.replace_handle(new_handle)

    Replace existing handle.

    :param new_handle: new handle as hex string, e.g. 'FFFF'

.. method:: Tags.dxftype()

    Returns DXF type of entity, e.g. 'LINE'.

.. method:: Tags.has_tag(code)

    Returns True if a DXF tag with group code `code` is present else False.

    :param int code: group code

.. method:: Tags.get_first_value(code, default=DXFValueError)

    Returns value of first DXF tag with given group `code` or default if default is not DXFValueError,
    else raises DXFValueError.

    :param int code: group code
    :param default: default value, DXFValueError raises an exception

.. method:: Tags.get_first_tag(code, default=DXFValueError)

    Returns first DXF tag with given group `code` or default if default is not DXFValueError,
    else raises DXFValueError.

    :param int code: group code
    :param default: default value, DXFValueError raises an exception

.. method:: Tags.find_all(code)

    Returns a list of DXF tag with given group `code`.

    :param int code: group code

.. method:: Tags.tag_index(code, start=0, end=None)

    Return index of first DXF tag with given group code.

    :param int code: group code
    :param int start: start index as int
    :param int end: end index as int, if None end index is length of :class:`Tags`

.. method:: Tags.update(tag)

    Update first existing `tag` with same group code as `tag`, raises DXFValueError if `tag` not exists.

    :param tag: new DXF tag with `code` property

.. method:: Tags.set_first(tag)

    Update first existing tag with same group code as `tag` or append `tag`.

    :param tag: DXF tag

.. method:: Tags.remove_tags(codes)

    Remove all tags inplace with group codes specified in `codes`.

    :param codes: iterable of group codes

.. method:: Tags.remove_tags_except(codes)

    Remove all tags inplace except those with group codes specified in `codes`.

    :param codes: iterable of group codes

.. method:: Tags.collect_consecutive_tags(codes, start=0, end=None)

    Collect all consecutive tags with group code in codes, start and end delimits the
    search range. A tag code not in codes ends the process.

    :param codes: iterable of group codes
    :param int start: start index
    :param int end: end index, if None end index is length of :class:`Tags`
    :return: collected tags as :class:`Tags` object


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


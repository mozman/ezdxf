
.. module:: ezdxf.urecord

Custom XRecord
==============

The :class:`UserRecord` and :class:`BinaryRecord` classes help to store
custom data in DXF files in :class:`~ezdxf.entities.XRecord` objects a simple
and safe way. This way requires DXF version R2000 or later, for DXF version
R12 the only way to store custom data is :ref:`extended_data`.

The :class:`UserRecord` stores Python types and nested container types:
``int``, ``float``, ``str``, :class:`~ezdxf.math.Vec2`, :class:`~ezdxf.math.Vec3`,
``list`` and ``dict``.

Requirements for Python structures:

- The top level structure has to be a ``list``.
- Strings has to have max. 2049 characters and can not contain line breaks
  ``"\\n"`` or ``"\\r"``.
- Dict keys have to be simple Python types: ``int``, ``float``, ``str``.

DXF Tag layout for Python types and structures stored in the
:class:`~ezdxf.entities.XRecord` object:

Only for the :class:`UserRecord` the first tag is (2, user record name).

=========== ===========================================================
Type        DXF Tag(s)
=========== ===========================================================
str         (1, value) string with less than 2050 chars and including no line breaks
int         (90, value) int 32-bit, restricted by the DXF standard not by Python!
float       (40, value) "C" double
Vec2        (10, x), (20, y)
Vec3        (10, x) (20, y) (30, z)
list        starts with (2, "[")  and ends with (2, "]")
dict        starts with (2, "{")  and ends with (2, "}")
=========== ===========================================================

The :class:`BinaryRecord` stores arbitrary binary data as `BLOB`_.

Storage size limits of XRECORD according the DXF reference:

    "This object is similar in concept to XDATA but is not limited by size or order."

For usage look at this `example`_ at github or go to the tutorial:
:ref:`tut_custom_data`.

.. seealso::

    - Tutorial: :ref:`tut_custom_data`
    - `Example`_ at github
    - :class:`ezdxf.entities.XRecord`

UserRecord
----------

.. class:: UserRecord

    .. attribute:: xrecord

        The underlying :class:`~ezdxf.entities.XRecord` instance

    .. attribute:: name

        The name of the :class:`UserRecord`, an arbitrary string with less than
        2050 chars and including no line breaks.

    .. attribute:: data

        The Python data. The top level structure has to be a list
        (:class:`MutableSequence`). Inside this container the following Python
        types are supported: str, int, float, Vec2, Vec3, list, dict

        Nested data structures are supported list or/and dict in list or dict.
        Dict keys have to be simple Python types: int, float, str.

    .. autoproperty:: handle

    .. automethod:: __init__

    .. automethod:: __str__

    .. automethod:: commit

BinaryRecord
------------

.. class:: BinaryRecord

    .. attribute:: xrecord

        The underlying :class:`~ezdxf.entities.XRecord` instance

    .. attribute:: data

        The binary data as bytes, bytearray or memoryview.

    .. autoproperty:: handle

    .. automethod:: __init__

    .. automethod:: __str__

    .. automethod:: commit


.. _BLOB: https://en.wikipedia.org/wiki/Binary_large_object

.. _example: https://github.com/mozman/ezdxf/blob/master/examples/user_data_stored_in_XRECORD.py
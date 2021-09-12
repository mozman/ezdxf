
.. module:: ezdxf.entities.xdata
    :noindex:

Custom XDATA
============

The classes :class:`XDataUserList` and :class:`XDataUserDict` manage
custom user data stored in the XDATA section of a DXF entity. For more
information about XDATA see reference section: :ref:`extended_data`

These classes store only a limited set of data types with fixed group codes and
the types are checked by :func:`isinstance` so a :class:`Vec3` object can not
be replaced by a (x, y, z)-tuple:

=========== ============
Group Code  Data Type
=========== ============
1000        str, limited to 255 characters, line breaks ``"\n"`` and ``"\r"``
            are not allowed
1010        Vec3
1040        float
1071        32bit int, restricted by the DXF standard not by Python!
=========== ============

Strings are limited to 255 characters, line breaks ``"\n"`` and ``"\r"`` are
not allowed.

This classes assume a certain XDATA structure and therefore can not manage
arbitrary XDATA!

This classes do not create the required AppID table entry, only the
default AppID "EZDXF" exist by default. Setup a new AppID in the AppID
table: :code:`doc.appids.add("MYAPP")`.

.. seealso::

    - XDATA reference: :ref:`extended_data`
    - XDATA management class: :class:`XData`
    - Tutorial: :ref:`tut_custom_data`

XDataUserList
-------------

.. class:: XDataUserList

    Manage user data as a named list-like object in XDATA. Multiple user lists
    with different names can be stored in a single :class:`XData` instance
    for a single AppID.

    Recommended usage by context manager :meth:`entity`::

        with XDataUserList.entity(entity, name="MyList", appid="MYAPP") as ul:
            ul.append("The value of PI")  # str "\n" and "\r" are not allowed
            ul.append(3.141592)  # float
            ul.append(1) # int
            ul.append(Vec3(1, 2, 3)) # Vec3

            # invalid data type raises DXFTypeError
            ul.append((1, 2, 3))  # tuple instead of Vec3

            # retrieve a single value
            s = ul[0]

            # store whole content into a Python list
            data = list(ul)


    Implements the :class:`MutableSequence` interface.

    .. attribute:: xdata

        The underlying :class:`XData` instance.

    .. automethod:: __init__

    .. automethod:: __str__

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: entity

    .. automethod:: commit

XDataUserDict
-------------

.. class:: XDataUserDict

    Manage user data as a named dict-like object in XDATA. Multiple user dicts
    with different names can be stored in a single :class:`XData` instance
    for a single AppID. The keys have to be strings.

    Recommended usage by context manager :meth:`entity`::

        with XDataUserDict.entity(entity, name="MyDict", appid="MYAPP") as ud:
            ud["comment"] = "The value of PI"  # str "\n" and "\r" are not allowed
            ud["pi"] = 3.141592  # float
            ud["number"] = 1 # int
            ud["vertex"] = Vec3(1, 2, 3) # Vec3

            # invalid data type raises DXFTypeError
            ud["vertex"] = (1, 2, 3)  # tuple instead of Vec3

            # retrieve single values
            s = ud["comment"]
            pi = ud.get("pi", 3.141592)

            # store whole content into a Python dict
            data = dict(ud)

    Implements the :class:`MutableMapping` interface.

    The data is stored in XDATA like a :class:`XDataUserList` by (key, value)
    pairs, therefore a :class:`XDataUserDict` can also be loaded as
    :class:`XDataUserList`. It is not possible to distinguish a
    :class:`XDataUserDict` from a :class:`XDataUserList` except by the name of
    the data structure.

    .. attribute:: xdata

        The underlying :class:`XData` instance.

    .. automethod:: __init__

    .. automethod:: __str__

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: discard

    .. automethod:: __iter__

    .. automethod:: entity

    .. automethod:: commit

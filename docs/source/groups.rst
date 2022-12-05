Groups
======

.. module:: ezdxf.entities.dxfgroups


A group is just a bunch of DXF entities tied together. All entities of a group
has to be in the same layout (modelspace or any paperspace layout but not block).
Groups can be named or unnamed, but in reality an unnamed groups has just a
special name like "\*Annnn". The name of a group has to be unique in the drawing.
Groups are organized in the group table, which is stored as attribute
:attr:`~ezdxf.document.Drawing.groups` in the :class:`~ezdxf.document.Drawing`
object.

.. important::

    Group entities have to reside in the modelspace or an paperspace layout but not in a
    block definition!

DXFGroup
--------

.. class:: DXFGroup

    The group name is not stored in the GROUP entity, it is stored in the
    :class:`GroupCollection` object.

    .. attribute:: dxf.description

        group description (string)

    .. attribute:: dxf.unnamed

        1 for unnamed, 0 for named group (int)

    .. attribute:: dxf.selectable

        1 for selectable, 0 for not selectable group (int)

    .. automethod:: __iter__

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __contains__

    .. automethod:: handles

    .. automethod:: edit_data

    .. automethod:: set_data

    .. automethod:: extend

    .. automethod:: clear

    .. automethod:: audit

GroupCollection
---------------

Each :class:`~ezdxf.document.Drawing` has one group table, which is accessible
by the attribute :attr:`~ezdxf.document.Drawing.groups`.

.. class:: GroupCollection

    Manages all :class:`DXFGroup` objects of a :class:`~ezdxf.document.Drawing`.

    .. method:: __len__

        Returns the count of DXF groups.

    .. method:: __iter__

        Iterate over all existing groups as (`name`, `group`) tuples. `name` is
        the name of the group as string and `group` is an :class:`DXFGroup`
        object.

    .. method:: __contains__

        Returns ``True`` if a group `name` exist.

    .. method:: get(name: str) -> DXFGroup

        Returns the group `name`. Raises :class:`DXFKeyError` if group `name`
        does not exist.

    .. automethod:: groups

    .. automethod:: new

    .. automethod:: delete

    .. method:: clear

       Delete all groups.

    .. automethod:: audit
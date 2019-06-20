Groups
======

A group is just a bunch of DXF entities tied together. All entities of a group has to be on the same layout (model space
or any paper layout but not block). Groups can be named or unnamed, but in reality an unnamed groups has just a special
name like ``*Annnn``. The name of a group has to be unique in the drawing. Groups are organized in the main group table,
which is stored as attribute :attr:`~ezdxf.drawing.Drawing.groups` in the :class:`~ezdxf.drawing.Drawing` object.

Group entities have to be in model space or any paper layout but not in a block definition!

.. class:: DXFGroup

    The group name is not stored in the GROUP entity, it is stored in the :class:`DXFGroupTable` object.

    .. attribute:: dxf.description

        group description (string)

    .. attribute:: dxf.unnamed

        ``1`` for unnamed, ``0`` for named group (int)

    .. attribute:: dxf.selectable

        ``1`` for selectable, ``0`` for not selectable group (int)

    .. method:: __iter__()

       Iterate over all DXF entities in this group as instances of :class:`GraphicEntity` or inherited (LINE, CIRCLE, ...).

    .. method:: __len__()

       Returns the count of DXF entities in this group.

    .. method:: __contains__(item)

       Returns `True` if item is in this group else `False`. `item` has to be a handle string or an object of type
       :class:`GraphicEntity` or inherited.

    .. method:: handles()

       Generator over all entity handles in this group.

    .. method:: get_name()

       Get name of the group as `string`.

    .. method:: edit_data()

       Context manager which yields all the group entities as standard Python list::

        with group.edit_data() as data:
           # add new entities to a group
           data.append(modelspace.add_line((0, 0), (3, 0)))
           # remove last entity from a group
           data.pop()

    .. method:: set_data(entities)

       Set `entities` as new group content, entities should be iterable and yields instances of :class:`GraphicEntity` or
       inherited (LINE, CIRCLE, ...).

    .. method:: extend(entities)

       Append `entities` to group content, entities should be iterable and yields instances of :class:`GraphicEntity` or
       inherited (LINE, CIRCLE, ...).

    .. method:: clear()

       Remove all entities from group.

    .. method:: remove_invalid_handles()

       Remove invalid handles from group. Invalid handles: deleted entities, entities in a block layout (but not implemented yet)


GroupTable
----------

There only exists one group table in each :class:`~ezdxf.drawing.Drawing`, which is accessible by the attribute
:attr:`~ezdxf.drawing.Drawing.groups`.

.. class:: DXFGroupTable

    .. method:: __iter__()

       Iterate over all existing groups as `(name, group)` tuples. `name` is the name of the group as `string` and `group`
       is an object of type :class:`DXFGroup`.

    .. method:: groups()

       Generator over all existing groups, yields just objects of type :class:`DXFGroup`.

    .. method:: __len__()

       Returns the count of DXF groups.

    .. method:: __contains__(name)

       Returns `True` if a group `name` exists else `False`.

    .. method:: get(name)

       Returns the group `name` as :class:`DXFGroup` object. Raises ``DXFKeyError`` if no group `name` exists.

    .. method:: new(name=None, description="", selectable=1)

       Creates a new group, returns a :class:`DXFGroup` object. If `name` is `None` an unnamed group is created, which has
       an automatically generated name like ``'*Annnn'``. `description` is the group description as string and `selectable`
       defines if the group is selectable (selectable=1) or not (selectable=0).

    .. method:: delete(group)

       Delete `group`. `group` can be an object of type :class:`DXFGroup` or a group name.


    .. method:: clear()

       Delete all groups.

    .. method:: cleanup()

       Removes invalid handles in all groups and empty groups.
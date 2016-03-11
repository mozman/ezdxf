Group
=====

A group is just a bunch of DXF entities tied together. All entities of a group has to be on the same layout (model space
or any paper layout but not block). Groups can be named or unnamed, but in reality an unnamed groups has just a special
name like ``'*Annnn'``. The name of a group has to be unique in the drawing. Groups are organized in the main group table,
which is an :attr:`Drawing.groups` of the class :class:`Drawing`.

Group entities have to be in model space or any paper layout but not in a block definition!

.. class:: DXFGroup

======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
description             R13     group description (string)
unnamed                 R13     1 for unnamed, 0 for named group (int)
selectable              R13     1 for selectable, 0 for not selectable group (int)
======================= ======= ===========

   The group name is not stored in the GROUP entity, it is stored in the :class:`DXFGroupTable` object.

.. method:: DXFGroup.__iter__()

   Iterate over all DXF entities in this group as instances of :class:`GraphicEntity` or inherited (LINE, CIRCLE, ...).

.. method:: DXFGroup.__len__()

   Returns the count of DXF entities in this group.

.. method:: DXFGroup.__contains__(item)

   Returns `True` if item is in this group else `False`. `item` has to be a handle string or an object of type
   :class:`GraphicEntity` or inherited.

.. method:: DXFGroup.handles()

   Generator over all entity handles in this group.

.. method:: DXFGroup.get_name()

   Get name of the group as `string`.

.. method:: DXFGroup.edit_data()

   Context manager which yields all the group entities as standard Python list::

    with group.edit_data() as data:
       # add new entities to a group
       data.append(modelspace.add_line((0, 0), (3, 0)))
       # remove last entity from a group
       data.pop()

.. method:: DXFGroup.set_data(entities)

   Set `entities` as new group content, entities should be iterable and yields instances of :class:`GraphicEntity` or
   inherited (LINE, CIRCLE, ...).

.. method:: DXFGroup.extend(entities)

   Append `entities` to group content, entities should be iterable and yields instances of :class:`GraphicEntity` or
   inherited (LINE, CIRCLE, ...).

.. method:: DXFGroup.clear()

   Remove all entities from group.

.. method:: DXFGroup.remove_invalid_handles()

   Remove invalid handles from group. Invalid handles: deleted entities, entities in a block layout (but not implemented yet)


GroupTable
==========

There only exists one group table in each drawing, which is accessible by the attribute :attr:`Drawing.groups`.

.. class:: DXFGroupTable

.. method:: DXFGroupTable.__iter__()

   Iterate over all existing groups as `(name, group)` tuples. `name` is the name of the group as `string` and `group`
   is an object of type :class:`DXFGroup`.

.. method:: DXFGroupTable.groups()

   Generator over all existing groups, yields just objects of type :class:`DXFGroup`.

.. method:: DXFGroupTable.__len__()

   Returns the count of DXF groups.

.. method:: DXFGroupTable.__contains__(name)

   Returns `True` if a group `name` exists else `False`.

.. method:: DXFGroupTable.get(name)

   Returns the group `name` as :class:`DXFGroup` object. Raises `KeyError` if no group `name` exists.

.. method:: DXFGroupTable.new(name=None, description="", selectable=1)

   Creates a new group, returns a :class:`DXFGroup` object. If `name` is `None` an unnamed group is created, which has
   an automatically generated name like ``'*Annnn'``. `description` is the group description as string and `selectable`
   defines if the group is selectable (selectable=1) or not (selectable=0).

.. method:: DXFGroupTable.delete(group)

   Delete `group`. `group` can be an object of type :class:`DXFGroup` or a group name.


.. method:: DXFGroupTable.clear()

   Delete all groups.

.. method:: DXFGroupTable.cleanup()

   Removes invalid handles in all groups and empty groups.
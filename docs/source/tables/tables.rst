Table Class
===========


Generic Table Class
-------------------

.. class:: Table

    Table entry names are case insensitive: 'Test' == 'TEST'.

.. method:: Table.new(name, dxfattribs=None)

:param str name: name of the new table-entry
:param dict dxfattribs: optional table-parameters, these parameters are described at the table-entry-classes below.
:returns: table-entry-class, can be ignored

Table entry creation is for all tables the same procedure::

    drawing.tablename.new(name, dxfattribs)

Where `tablename` can be: `layers`, `styles`, `linetypes`, `views`, `viewports`
or `dimstyles`.



.. method:: Table.get(name)

Get table-entry `name`. Raises ``DXFValueError`` if table-entry is not
present.

.. method:: Table.remove(name)

Removes table-entry `name`. Raises ``DXFValueError`` if table-entry is not
present.

.. method:: Table.__len__()

Get count of table-entries.

.. method:: Table.has_entry(name)

`True` if table contains a table-entry `name`.

.. method:: Table.__contains__(name)

`True` if table contains a table-entry `name`.

.. method:: Table.__iter__()

Iterate over all table.entries, yields table-entry-objects.

Style Table Class
-----------------

.. class:: StyleTable(Table)

.. method:: StyleTable.get_shx(name)

Get existing shx entry, or create a new entry.

.. method:: StyleTable.find_shx(name)

Find .shx shape file table entry, by a case insensitive search. A .shx shape file table entry has no name, so you
have to search by the font attribute.

Viewport Table Class
--------------------

.. class:: ViewportTable(Table)

The viewport table stores the model space viewport configurations. A viewport configuration is a tiled view of multiple
viewports or just one viewport. In contrast to other tables the viewport table can have multiple entries with the same
name, because all viewport entries of a multi-viewport configuration are having the same name - the viewport
configuration name.

The name of the actual displayed viewport configuration is "\*ACTIVE".

.. method:: ViewportTable.get_config(name)

Returns a list of :class:`Viewport` objects, of the multi-viewport configuration *name*.

.. method:: ViewportTable.delete_config(name):

Delete all :class:`Viewport` objects of the multi-viewport configuration *name*.

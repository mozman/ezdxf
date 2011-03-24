Table Class
===========

.. class:: Table

.. method:: Table.create(name, attribs=None)

    :param str name: name of the new table-entry
    :param dict attribs: optional table-parameters, these parameters are described at the table-entry-classes below.
    :returns: table-entry-class, can be ignored

Table entry creation is for all tables the same procedure::

    drawing.tablename.create(name, attribs)

Where `tablename` can be: `layers`, `styles`, `linetypes`, `views`, `viewports`
or `dimstyles`.

.. method:: Table.get(name)

    Get table-entry `name`. Raises `ValueError` if table-entry is not
    present.

.. method:: Table.remove(name)

    Removes table-entry `name`. Raises `ValueError` if table-entry is not
    present.

.. method:: Table.__len__()

    Get count of table-entries.

.. method:: Table.__contains__(name)

    `True` if table contains a table-entry named `name`.

.. method:: Table.__iter__()

    Iterate over all table.entries, yields table-entry-objects.

Table Entry Classes
===================

.. class:: Layer

.. class:: Style

.. class:: Linetype

.. class:: Viewport

.. class:: View

.. class:: DimStyle


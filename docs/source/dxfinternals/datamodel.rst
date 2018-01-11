Data Model
==========

.. _Database Objects:

Database Objects
----------------

(from the DXF Reference)

AutoCAD drawings consist largely of structured containers for database objects. Database objects each have the following
features:

- A handle whose value is unique to the drawing/DXF file, and is constant for the lifetime of the drawing. This format
  has existed since AutoCAD Release 10, and as of AutoCAD Release 13, handles are always enabled.
- An optional xdata table, as entities have had since AutoCAD Release 11.
- An optional persistent reactor table.
- An optional ownership pointer to an extension dictionary which, in turn, owns subobjects placed in it by an application.

Symbol tables and symbol table records are database objects and, thus, have a handle. They can also have xdata and
persistent reactors in their DXF records.



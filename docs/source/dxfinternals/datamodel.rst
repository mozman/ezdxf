.. _DataModel:

Data Model
==========

.. _Database Objects:

Database Objects
----------------

(from the DXF Reference)

AutoCAD drawings consist largely of structured containers for database objects. Database objects each have the following
features:

    - A handle whose value is unique to the drawing/DXF file, and is constant for the lifetime of the drawing. This
      format has existed since AutoCAD Release 10, and as of AutoCAD Release 13, handles are always enabled.
    - An optional xdata table, as entities have had since AutoCAD Release 11.
    - An optional persistent reactor table.
    - An optional ownership pointer to an extension dictionary which, in turn, owns subobjects placed in it by an
      application.

Symbol tables and symbol table records are database objects and, thus, have a handle. They can also have xdata and
persistent reactors in their DXF records.


DXF R12 Data Model
------------------

The DXF R12 data model is identical to the file structure:

    - HEADER section: common settings for the DXF drawing
    - TABLES section: definitions for LAYERS, LINETYPE, STYLES ....
    - BLOCKS section: block definitions and its content
    - ENTITIES section: model space and paper space content

References are realized by simple names. The INSERT entity references the BLOCK definition by the BLOCK name, a TEXT
entity defines the associated STYLE and LAYER by its name and so on, handles are not needed. Layout association of
graphical entities in the ENTITIES section by the paper_space tag :code:`(67, 0 or 1)`, 0 or missing tag means model
space, 1 means paper space. The content of BLOCK definitions is enclosed by the BLOCK and the ENDBLK entity, no
additional references are needed.

A clean and simple file structure and data model, which seems to be the reason why the DXF R12 Reference (released 1992)
is still a widely used file format and Autodesk/AutoCAD supports the format by reading and writing DXF R12 files until
today (DXF R13/R14 has no writing support by AutoCAD!).

.. seealso::

    More information about the DXF :ref:`File Structure`

DXF R13 and later Data Model
----------------------------

It's getting complicated!
TODO ;-)

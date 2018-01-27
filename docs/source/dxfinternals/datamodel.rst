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

DXF R13+ Data Model
-------------------

It's getting complicated!

With the DXF R13 file format, handles are mandatory and they are really used for organizing the new data structures
introduced with DXF R13.

The first important new feature is the OBJECTS sections, which stores all the none graphical entities of the DXF drawing.
None graphical entities from now on just called 'objects' to differentiate from graphical entities, which will just
called 'entities'. The OBJECTS section follows commonly the ENTITIES section, but this is not mandatory. DXF R13
introduces also several new DXF object which resides exclusive in the OBJECTS section, taken from the DXF R14 reference,
because I have no access to the DXF R13 reference, the DXF R13 reference is a compiled .hlp file which can't be read on
Windows 10, a drastic real world example why it is better to avoid closed (proprietary) data formats ;-):

    - DICTIONARY: a general structural entity as a (key: value) store, exactly it is a (name: handle) container
    - ACDBDICTIONARYWDFLT: a DICTIONARY with a default value
    - DICTIONARYVAR: are used by AutoCAD to store named values in the database
    - ACAD_PROXY_OBJECT
    - GROUP: group graphical entities without the need of a BLOCK definition
    - IDBUFFER: just a list of references to objects
    - IMAGEDEF: IMAGE definition structure, required by the IMAGE entity
    - IMAGEDEF_REACTOR: also required by the IMAGE entity
    - LAYER_INDEX: container for LAYER names
    - MLINESTYLE
    - OBJECT_PTR
    - RASTERVARIABLES
    - SPATIAL_INDEX: is always written out empty to a DXF file. This object can be ignored.
    - SPATIAL_FILTER
    - SORTENTSTABLE: control for regeneration/redraw order of entities
    - XRECORD: are used to store and manage arbitrary data. This object is similar in concept to XDATA but is not
      limited by size or order. Not supported by R13c0 through R13c3.

Still missing the LAYOUT object, which is mandatory in DXF R2000 to manage multiple paper space layouts. I don't know
how DXF R13/R14 manages multiple layouts or if they even support it, but I don't care much about DXF R13/R14, because
AutoCAD has no write support for this two formats anymore. ezdxf tries to upgrade this two DXF versions to DXF R2000
with the advantage of only two different data models to support: DXF R12 and DXF R2000+

New objects introduced by DXF R2000:

    - LAYOUT: management object for model space and multiple paper space layouts
    - ACDBPLACEHOLDER: surprise - just a place holder

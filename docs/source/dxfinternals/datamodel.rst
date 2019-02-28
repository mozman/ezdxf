.. _Data Model:

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

.. _DXF R12 Data Model:

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

**TODO: list of available entities**

.. seealso::

    More information about the DXF :ref:`File Structure`

.. _DXF R13+ Data Model:

DXF R13+ Data Model
-------------------

With the DXF R13 file format, handles are mandatory and they are really used for organizing the new data structures
introduced with DXF R13.

The HEADER section is still the same with just more available settings.

The new CLASSES section contains AutoCAD specific data, has to be written like AutoCAD it does, but must not be
understood.

The TABLES section got a new BLOCK_RECORD table - see :ref:`Block Management Structures` for more information.

The BLOCKS sections is mostly the same, but with handles, owner tags and new ENTITY types. Not active paper space
layouts store their content also in the BLOCKS section - see :ref:`Layout Management Structures` for more information.

The ENTITIES section is also mostly same, but with handles, owner tags and new ENTITY types.

**TODO: list of new available entities**

And the new OBJECTS section - now its getting complicated!

Most information about the OBJECTS section is just guessed or gathered by trail and error, because
the documentation of the OBJECTS section and its objects in the DXF reference provided by Autodesk is very shallow.
This is also the reason why I started the DXF Internals section, may be it helps other developers to start one or two
steps above level zero.

The OBJECTS sections stores all the non-graphical entities of the DXF drawing.
Non-graphical entities from now on just called 'DXF objects' to differentiate them from graphical entities, just called
'entities'. The OBJECTS section follows commonly the ENTITIES section, but this is not mandatory.

DXF R13 introduces several new DXF objects, which resides exclusive in the OBJECTS section, taken from the DXF R14
reference, because I have no access to the DXF R13 reference, the DXF R13 reference is a compiled .hlp file which can't
be read on Windows 10, a drastic real world example why it is better to avoid closed (proprietary) data formats ;):

    - DICTIONARY: a general structural entity as a <name: handle> container
    - ACDBDICTIONARYWDFLT: a DICTIONARY with a default value
    - DICTIONARYVAR: used by AutoCAD to store named values in the database
    - ACAD_PROXY_OBJECT: proxy object for entities created by other applications than AutoCAD
    - GROUP: groups graphical entities without the need of a BLOCK definition
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
    - XRECORD: used to store and manage arbitrary data. This object is similar in concept to XDATA but is not
      limited by size or order. Not supported by R13c0 through R13c3.

Still missing the LAYOUT object, which is mandatory in DXF R2000 to manage multiple paper space layouts. I don't know
how DXF R13/R14 manages multiple layouts or if they even support this feature, but I don't care much about DXF R13/R14,
because AutoCAD has no write support for this two formats anymore. ezdxf tries to upgrade this two DXF versions to DXF
R2000 with the advantage of only two different data models to support: DXF R12 and DXF R2000+

New objects introduced by DXF R2000:

    - LAYOUT: management object for model space and multiple paper space layouts
    - ACDBPLACEHOLDER: surprise - just a place holder

New objects in DXF R2004:

    - DIMASSOC
    - LAYER_FILTER
    - MATERIAL
    - PLOTSETTINGS
    - VBA_PROJECT

New objects in DXF R2007:

    - DATATABLE
    - FIELD
    - LIGHTLIST
    - RENDER
    - RENDERENVIRONMENT
    - MENTALRAYRENDERSETTINGS
    - RENDERGLOBAL
    - SECTION
    - SUNSTUDY
    - TABLESTYLE
    - UNDERLAYDEFINITION
    - VISUALSTYLE
    - WIPEOUTVARIABLES

New objects in DXF R2013:

    - GEODATA

New objects in DXF R2018:

    - ACDBNAVISWORKSMODELDEF

Undocumented objects:

    - SCALE
    - ACDBSECTIONVIEWSTYLE
    - FIELDLIST

.. _Object Organisation:

Objects Organisation
--------------------

Many objects in the OBJECTS section are organized in a tree-like structure of DICTIONARY objects.
Starting point for this data structure is the 'root' DICTIONARY with several entries to other DICTIONARY objects.
The root DICTIONARY has to be the first object in the OBJECTS section. The management dicts for GROUP and LAYOUT objects
are really important, but IMHO most of the other management tables are optional and for the most use cases not
necessary. The ezdxf template for DXF R2018 contains only these entries in the root dict and most of them pointing to
an empty DICTIONARY:

    - ACAD_COLOR: points to an empty DICTIONARY
    - **ACAD_GROUP:** supported by ezdxf
    - **ACAD_LAYOUT:** supported by ezdxf
    - ACAD_MATERIAL: points to an empty DICTIONARY
    - ACAD_MLEADERSTYLE: points to an empty DICTIONARY
    - ACAD_MLINESTYLE: points to an empty DICTIONARY
    - ACAD_PLOTSETTINGS: points to an empty DICTIONARY
    - **ACAD_PLOTSTYLENAME:** points to ACDBDICTIONARYWDFLT with one entry: 'Normal'
    - ACAD_SCALELIST: points to an empty DICTIONARY
    - ACAD_TABLESTYLE: points to an empty DICTIONARY
    - ACAD_VISUALSTYLE: points to an empty DICTIONARY

.. _Root DICTIONARY:

Root DICTIONARY content for DXF R2018
-------------------------------------

.. code-block:: none

    0
    SECTION
    2       <<< start of the OBJECTS section
    OBJECTS
    0       <<< root DICTIONARY has to be the first object in the OBJECTS section
    DICTIONARY
    5       <<< handle
    C
    330     <<< owner tag
    0       <<< always #0, has no owner
    100
    AcDbDictionary
    281     <<< hard owner flag
    1
    3       <<< first entry
    ACAD_CIP_PREVIOUS_PRODUCT_INFO
    350     <<< handle to target (pointer)
    78B     <<< points to a XRECORD with product info about the creator application
    3       <<< entry with unknown meaning, if I shoul guess: something with about colors ...
    ACAD_COLOR
    350
    4FB     <<< points to a DICTIONARY
    3       <<< entry with unknown meaning
    ACAD_DETAILVIEWSTYLE
    350
    7ED     <<< points to a DICTIONARY
    3       <<< GROUP management, mandatory in all DXF versions
    ACAD_GROUP
    350
    4FC     <<< points to a DICTIONARY
    3       <<< LAYOUT management, mandatory if more than the *active* paper space is used
    ACAD_LAYOUT
    350
    4FD     <<< points to a DICTIONARY
    3       <<< MATERIAL management
    ACAD_MATERIAL
    350
    4FE     <<< points to a DICTIONARY
    3       <<< MLEADERSTYLE management
    ACAD_MLEADERSTYLE
    350
    4FF     <<< points to a DICTIONARY
    3       <<< MLINESTYLE management
    ACAD_MLINESTYLE
    350
    500     <<< points to a DICTIONARY
    3       <<< PLOTSETTINGS management
    ACAD_PLOTSETTINGS
    350
    501     <<< points to a DICTIONARY
    3       <<< plot style name management
    ACAD_PLOTSTYLENAME
    350
    503     <<< points to a ACDBDICTIONARYWDFLT
    3       <<< SCALE management
    ACAD_SCALELIST
    350
    504     <<< points to a DICTIONARY
    3       <<< entry with unknown meaning
    ACAD_SECTIONVIEWSTYLE
    350
    7EB     <<< points to a DICTIONARY
    3       <<< TABLESTYLE management
    ACAD_TABLESTYLE
    350
    505     <<< points to a DICTIONARY
    3       <<< VISUALSTYLE management
    ACAD_VISUALSTYLE
    350
    506     <<< points to a DICTIONARY
    3       <<< entry with unknown meaning
    ACDB_RECOMPOSE_DATA
    350
    7F3
    3       <<< entry with unknown meaning
    AcDbVariableDictionary
    350
    7AE     <<< points to a DICTIONARY with handles to DICTIONARYVAR objects
    0
    DICTIONARY
    ...
    ...
    0
    ENDSEC

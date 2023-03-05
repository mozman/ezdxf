.. _dxf_entities_concept:

DXF Entities and Objects
========================

DXF entities are objects that make up the design data stored in a DXF file.

Graphical Entities
------------------

Graphical entities are visible objects stored in blocks, modelspace- or paperspace
layouts. They represent the various shapes, lines, and other elements that make up a
2D or 3D design.

Some common types of DXF entities include:

- LINE and POLYLINE: These are the basic building blocks of a DXF file. They
  represent straight and curved lines.
- CIRCLE and ARC: These entities represent circles and portions of circles, respectively.
- TEXT and MTEXT: DXF files can also contain text entities, which can be used to
  label parts of the design or provide other information.
- HATCH: DXF files can also include hatch patterns, which are used to fill in areas with
  a specific pattern or texture.
- DIMENSION: DXF files can also contain dimension entities, which provide precise
  measurements of the various elements in a design.
- INSERT: A block is a group of entities that can be inserted into a design multiple
  times by the INSERT entity, making it a useful way to reuse elements of a design.

These entities are defined using specific codes and values in the DXF file format, and
they can be created, manipulated and edited by `ezdxf`.

Objects
-------

DXF objects are non-graphical entities and have no visual representation, they store
administrative data, paperspace layout definitions, style definitions for multiple
entity types, custom data and objects. The OBJECTS section in DXF files serves as a
container for these non-graphical objects.

Some common DXF types of DXF objects include:

- DICTIONARY: A dictionary object consists of a series of name-value pairs, where the
  name is a string that identifies a specific object within the dictionary, and the
  value is a reference to that object. The objects themselves can be any type of DXF
  entity or custom object defined in the DXF file.
- XRECORD entities are used to store custom application data in a DXF file.
- the LAYOUT entity is a DXF entity that represents a single paper space layout in a DXF
  file. Paper space is the area in a CAD drawing that represents the sheet of paper or
  other physical media on which the design will be plotted or printed.
- MATERIAL, MLINESTYLE, MLEADERSTYLE definitions stored in certain DICTIONARY objects.
- A GROUP entity contains a list of handles that refer to other DXF entities in the
  drawing. The entities in the group can be of any type, including entities from the
  model space or paper space layouts.

TagStorage
----------

The `ezdxf` package supports many but not all entity types, all these unsupported
types are stored as :class:`TagStorage` instances to preserver their data when
exporting the edited DXF content.

Access Entity Attributes
------------------------

All DXF attributes are stored in the entity namespace attribute :attr:`dxf`.

.. code-block:: Python

    print(entity.dxf.layer)

Some attributes are mandatory others are optional in most cases a reasonable values will
be returned as default value if the attribute is missing.

Where to Look for Entities
--------------------------

The DXF document has an entity database where all entities which have a handle are
stored in a (key, value) storage. The :meth:`query` method is often the easiest way to
request data:

.. code-block:: Python

    for text in doc.entitydb.query("TEXT"):
        print(text.dxf.text)

For more information about entity queries read the documentation about the
:mod:`ezdxf.query` module.

Graphical entities are stored in blocks, the modelspace or paperspace layouts.


- The :func:`doc.modelspace` function returns the :class:`~ezdxf.layouts.Modelspace` instance
- The :func:`doc.paperspace` returns a :class:`~ezdxf.layouts.Paperspace` instance
- The :attr:`doc.blocks` attribute provides access to the :class:`~ezdxf.sections.blocks.BlocksSection`

Non-graphical entities are stored in the OBJECTS section:

- The :attr:`doc.objects` attribute provides access to the
  :class:`~ezdxf.sections.objects.ObjectsSection`.

Table entries are stored in resource tables:

- :attr:`doc.layers`: the :class:`~ezdxf.sections.table.LayerTable`
- :attr:`doc.linetypes`: the :class:`~ezdxf.sections.table.LinetypeTable`
- :attr:`doc.styles`: the :class:`~ezdxf.sections.table.TextstyleTable`
- :attr:`doc.dimstyles`: the :class:`~ezdxf.sections.table.DimStyleTable`


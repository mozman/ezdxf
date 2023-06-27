.. _external_references:

.. module:: ezdxf.xref

External References (XREF)
==========================

.. versionadded:: 1.1

Attached XREFs are links to the modelspace of a specified drawing file. Changes made
to the referenced drawing are automatically reflected in the current drawing when it's
opened or if the XREF is reloaded.

XREFs can be nested within other XREFs: that is, you can attach an XREF that contains
another XREF. You can attach as many copies of an XREF as you want, and each copy can
have a different position, scale, and rotation.

You can also overlay an XREF on your drawing. Unlike an attached XREF, an overlaid XREF
is not included when the drawing is itself attached or overlaid as an XREF to another
drawing.

DXF Files as Attached XREFs
---------------------------

.. important::

    AutoCAD can only display DWG files as attached XREFs but `ezdxf` can only create
    DXF files.  Consequently, any DXF file attached as an XREF to a DXF document must
    be converted to DWG in order to be viewed in AutoCAD.
    Fortunately, other CAD applications are more cooperative, BricsCAD has no problem
    displaying DXF files as XREFs, although it is not possible to attach a DXF file as an
    XREF in the BricsCAD application itself.

The :mod:`ezdxf.xref` module provides an interface for working with XREFs.

    - :func:`attach` - attach a DXF/DWG file as XREF
    - :func:`detach` - detach a BLOCK definition as XREF
    - :func:`embed` - embed an XREF as a BLOCK definition
    - :func:`dxf_info` - scans a DXF file for basic settings and properties

For loading the content of DWG files is a loading function required, which loads the
DWG file as :class:`Drawing` document. The :mod:`~ezdxf.addons.odafc` add-on module
provides such a function: :func:`~ezdxf.addons.odafc.readfile`

.. seealso::

    - :ref:`tut_xref_module`

XREF Structures
---------------

An XREF is a normal block definition located in the BLOCKS section with special flags
set and a filename to the referenced DXF/DWG file and without any content, the block
content is the modelspace of the referenced file.  An XREF can be referenced (inserted)
by one or multiple INSERT entities.

Find block definitions in the BLOCKS section:

.. code-block:: Python

    for block_layout in doc.blocks:
        block = block_layout.block  # the BLOCK entity
        if block.is_xref:
            handle_xref(block_layout)
        elif block.is_xref_overlay:
            handle_xref_overlay(block_layout)

Find XREF references in modelspace:

.. code-block:: Python

    for insert in msp.query("INSERT"):
        if insert.is_xref:
            handle_xref_reference(insert)
            # ... or get the XREF definition
            block_layout = insert.block()
            if block_layout is not None:
                handle_xref_definition(block_layout)

Use the helper function :func:`define` to create your own XREF definition, the
:func:`attach` creates this definition automatically and raises an exception if the
block already exists.

Supported Entities
------------------

The current implementation supports only copyable and transformable DXF entities,
these are all basic entity types as LINE, CIRCLE, ... and block references and their
associated required table entries and objects from the OBJECTS section.

Unsupported are all ACIS based entities, the ACAD_TABLE entity, preserved unknown entities
wrapped in a :class:`DXFTagStorage` class, proxy entities and objects.
Support for these entities may be added in a later version of `ezdxf`.

Unsupported entities are ignored and do not raise exceptions.

Importing Data and Resources
----------------------------

The :mod:`ezdxf.xref` module replaces the :class:`~ezdxf.addons.importer.Importer` add-on.

The basic functionality of the :mod:`ezdxf.xref` module is loading data from external
files including their required resources, which is an often requested feature by users
for importing data from other DXF files into the current document.

The :class:`Importer` add-on was very limited and removed many resources,
where the :mod:`ezdxf.xref` module tries to preserve as much information as possible.

    - :func:`load_modelspace` - loads the modelspace content from another DXF document
    - :func:`load_paperspace` - loads a paperspace layout from another DXF document
    - :func:`write_block` - writes entities into the modelspace of a new DXF document
    - :class:`Loader` - low level loading interface

High Level Functions
--------------------

.. autofunction:: attach

.. autofunction:: define

.. autofunction:: detach

.. autofunction:: dxf_info

.. autofunction:: embed

.. autofunction:: load_modelspace

.. autofunction:: load_paperspace

.. autofunction:: write_block

Conflict Policy
---------------

.. class:: ConflictPolicy

    .. attribute:: KEEP

    .. attribute:: XREF_PREFIX

    .. attribute:: NUM_PREFIX

Low Level Loading Interface
---------------------------

.. autoclass:: Loader


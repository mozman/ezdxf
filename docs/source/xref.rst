.. _external_references:

.. module:: ezdxf.xref

External References (XREF)
==========================

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

AutoCAD can only display DWG files as attached XREFs, which is a problem since `ezdxf`
can only create DXF files. Consequently, any DXF file attached as XREF to a DXF
document has be converted to DWG in order to be viewed in AutoCAD.

Fortunately, other CAD applications are more cooperative, so BricsCAD has no problem
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


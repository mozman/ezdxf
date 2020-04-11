.. module:: ezdxf.addons.importer
    :noindex:

.. _importer:

Importer
========

This add-on is meant to import graphical entities from another DXF drawing and their required table entries like LAYER,
LTYPE or STYLE.

Because of complex extensibility of the DXF format and the lack of sufficient documentation, I decided to remove most
of the possible source drawing dependencies from imported entities, therefore imported entities may not look
the same as the original entities in the source drawing, but at least the geometry should be the same and the DXF file
does not break.

Removed data which could contain source drawing dependencies: Extension Dictionaries, AppData and XDATA.

.. warning::

    DON'T EXPECT PERFECT RESULTS!

The :class:`Importer` supports following data import:

  - entities which are really safe to import: LINE, POINT, CIRCLE, ARC, TEXT, SOLID, TRACE, 3DFACE, SHAPE, POLYLINE,
    ATTRIB, ATTDEF, INSERT, ELLIPSE, MTEXT, LWPOLYLINE, SPLINE, HATCH, MESH, XLINE, RAY, DIMENSION, LEADER, VIEWPORT
  - table and table entry import is restricted to LAYER, LTYPE, STYLE, DIMSTYLE
  - import of BLOCK definitions is supported
  - import of paper space layouts is supported


Import of DXF objects from the OBJECTS section is not supported.

DIMSTYLE override for entities DIMENSION and LEADER is not supported.

Example:

.. code-block:: Python

    import ezdxf
    from ezdxf.addons import Importer

    sdoc = ezdxf.readfile('original.dxf')
    tdoc = ezdxf.new()

    importer = Importer(sdoc, tdoc)

    # import all entities from source modelspace into modelspace of the target drawing
    importer.import_modelspace()

    # import all paperspace layouts from source drawing
    importer.import_paperspace_layouts()

    # import all CIRCLE and LINE entities from source modelspace into an arbitrary target layout.
    # create target layout
    tblock = tdoc.blocks.new('SOURCE_ENTS')
    # query source entities
    ents = sdoc.modelspace().query('CIRCLE LINE')
    # import source entities into target block
    importer.import_entities(ents, tblock)

    # This is ALWAYS the last & required step, without finalizing the target drawing is maybe invalid!
    # This step imports all additional required table entries and block definitions.
    importer.finalize()

    tdoc.saveas('imported.dxf')



.. autoclass:: Importer
    :members:



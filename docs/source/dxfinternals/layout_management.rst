.. _Layout Management Structures:

Layout Management Structures
============================

Layouts are separated entity spaces, there are three different Layout types:

    1. Model space contains the 'real' world representation of the drawing subject in real world units.
    2. Paper space are used to create different drawing sheets of the subject for printing or PDF export
    3. Blocks are reusable sets of graphical entities, inserted by the INSERT entity.

All layouts have at least a BLOCK definition in the BLOCKS section and since DXF R13 exists the BLOCK_RECORD table with
an entry for every BLOCK in the BLOCKS section.

.. seealso::

    Information about :ref:`Block Management Structures`


The name of the model space BLOCK is ``*Model_Space`` (DXF R12: ``$MODEL_SPACE``) and the name of the `active` paper
space BLOCK is ``*Paper_Space`` (DXF R12: ``$PAPER_SPACE``), the entities of these two layouts are
stored in the ENTITIES section, DXF R12 supports just one paper space layout.

DXF R13 and later supports multiple paper space layouts, the `active` layout is still called ``*Paper_Space``, the
additional `inactive` paper space layouts are named by the scheme ``*Paper_Spacennnn``, where the first inactive paper
space is called ``*Paper_Space0``, the second ``*Paper_Space1`` and so on.
A none consecutive numbering is tolerated by AutoCAD. The content of the inactive paper space layouts are stored
as BLOCK content in the BLOCKS section. This names are just the DXF internal layout names, each layout has an
additional name which is displayed to the user by the CAD application.

A BLOCK definition and a BLOCK_RECORD is not enough for a proper layout setup, an LAYOUT entity in the OBJECTS section
is also required. All LAYOUT entities are managed by a DICTIONARY entity, which is referenced as ``ACAD_LAYOUT`` entity
in the root DICTIONARY of the DXF file.



.. _blocks_section_internals:

BLOCKS Section
==============

The BLOCKS section contains all BLOCK definitions, beside the 'normal' reusable
BLOCKS used by the INSERT entity, all layouts, as there are the modelspace and
all paperspace layouts, have at least a corresponding BLOCK definition in the
BLOCKS section. The name of the modelspace BLOCK is "*Model_Space" (DXF R12:
"$MODEL_SPACE") and the name of the `active` paperspace BLOCK is ""*Paper_Space"
(DXF R12: "$PAPER_SPACE"), the entities of these two layouts are stored
in the ENTITIES section, the `inactive` paperspace layouts are named by the
scheme "*Paper_Spacennnn", and the content of the inactive paperspace layouts
are stored in their BLOCK definition in the BLOCKS section.

The content entities of blocks are stored between the BLOCK and the ENDBLK
entity.

BLOCKS section structure:

.. code-block:: none

    0           <<< start of a SECTION
    SECTION
    2           <<< start of BLOCKS section
    BLOCKS
    0           <<< start of 1. BLOCK definition
    BLOCK
    ...         <<< Block content
    ...
    0           <<< end of 1. Block definition
    ENDBLK
    0           <<< start of 2. BLOCK definition
    BLOCK
    ...         <<< Block content
    ...
    0           <<< end of 2. Block definition
    ENDBLK
    0           <<< end of BLOCKS section
    ENDSEC

.. seealso::

    :ref:`Block Management Structures`
    :ref:`Layout Management Structures`


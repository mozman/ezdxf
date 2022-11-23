Blocks Section
==============

.. module:: ezdxf.sections.blocks

The BLOCKS section is the home all block definitions (:class:`~ezdxf.layouts.BlockLayout`)
of a DXF document.

.. warning::

    Blocks are an essential building block of the DXF format. Most block references
    are by name, and renaming or deleting a block is not as easy as it seems,
    since there is no overall index where all block references appear, and such
    references can also reside in custom data or even custom entities,
    therefore renaming or deleting block definitions can damage DXF files!

.. seealso::

    DXF Internals: :ref:`blocks_section_internals` and :ref:`Block Management Structures`

.. class:: BlocksSection

    .. automethod:: __iter__

    .. automethod:: __contains__

    .. automethod:: __getitem__

    .. automethod:: __delitem__

    .. automethod:: get

    .. automethod:: new

    .. automethod:: new_anonymous_block

    .. automethod:: rename_block

    .. automethod:: delete_block

    .. automethod:: delete_all_blocks



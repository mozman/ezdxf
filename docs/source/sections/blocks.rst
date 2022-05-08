Blocks Section
==============

.. module:: ezdxf.sections.blocks

The BLOCKS section is the home all block definitions (:class:`~ezdxf.layouts.BlockLayout`) of a DXF document.

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



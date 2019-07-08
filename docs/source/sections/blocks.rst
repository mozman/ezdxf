Blocks Section
==============

.. module:: ezdxf.sections.blocks

The BLOCKS section is the home all block definitions (:class:`~ezdxf.layouts.BlockLayout`) of a DXF document.

.. seealso::

    DXF Internals: :ref:`blocks_section_internals` and :ref:`Block Management Structures`

.. class:: BlocksSection

    .. automethod:: __iter__()  -> Iterable[BlockLayout]

    .. automethod:: __contains__

    .. automethod:: __getitem__(name: str) -> BlockLayout

    .. automethod:: __delitem__

    .. automethod:: get(self, name: str, default=None) -> BlockLayout

    .. automethod:: new(name: str, base_point: Sequence[float] = (0, 0), dxfattribs: dict = None) -> BlockLayout

    .. automethod:: new_anonymous_block(type_char: str = 'U', base_point: Sequence[float] = (0, 0)) -> BlockLayout

    .. automethod:: rename_block

    .. automethod:: delete_block

    .. automethod:: delete_all_blocks


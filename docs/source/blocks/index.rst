.. _blocks:

Blocks
======

A block definition (:class:`~ezdxf.layouts.BlockLayout`) is a collection of DXF entities,
which can be placed multiply times at different layouts or other blocks as references to
the block definition. Block layouts are located in the BLOCKS sections and are
accessible by the :attr:`~ezdxf.document.Drawing.blocks` attribute of the
:class:`~ezdxf.document.Drawing` class.

.. seealso::

    :ref:`tut_blocks` and DXF Internals: :ref:`Block Management Structures`

.. toctree::
    :maxdepth: 1

    block
    insert
    attrib
    attdef


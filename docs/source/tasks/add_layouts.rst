.. _add_layouts:

Add Layouts And Blocks
======================

Layouts are containers for DXF entities like LINE or CIRCLE. 
There exist three layouts types:

- :ref:`modelspace_concept`
- :ref:`paperspace_concept`
- :ref:`block_concept`

Modelspace
----------

The :class:`~ezdxf.layouts.Modelspace` is unique.
It is not possible to create another one.

Paperspace Layout
-----------------

All DXF versions can have multiple paperspace layouts expect DXF R12.

Add a new paperspace layout to a DXF document::

    doc.layouts.new("MyLayout")

The layout name is the name shown on the tab in CAD applications and has to be unique, 
otherwise a :class:`DXFValueError` will be raised. 

It is possible to add multiple paperspace layouts to all DXF versions, but `ezdxf` 
exports for DXF R12 only the active paperspace layout.  Any paperspace layout can be 
set as the active paperspace layout by the method: :meth:`ezdxf.layouts.Layouts.set_active_layout`.

- :meth:`ezdxf.layouts.Layouts.new`

Block Definition
----------------

Add a new block definition to a DXF document::

    doc.blocks.new("MyLayout")

The block name has to be unique, otherwise a :class:`DXFValueError` will be raised. 

Add an anonymous block definition::

    my_block = doc.blocks.new_anonymous_block()
    # store the block name, so you can create block references to this block
    block_name = my_block.name

Anonymous blocks are used internally and do not show up in the insert dialog for block 
references in CAD applications.

- :meth:`ezdxf.sections.blocks.BlocksSection.new`
- :meth:`ezdxf.sections.blocks.BlocksSection.new_anonymous_block`

.. seealso::

    **Tasks:**

    - :ref:`get_layouts`
    - :ref:`delete_layouts`
    - :ref:`add_dxf_entities`
    - :ref:`copy_or_move_entities`
    - :ref:`delete_dxf_entities`
    - :ref:`add_blockrefs`

    **Tutorials:**

    - :ref:`tut_getting_data`
    - :ref:`tut_blocks`
    - :ref:`tut_simple_drawings`
    - :ref:`tut_psp_viewports`

    **Basics:**

    - :ref:`layout`
    - :ref:`modelspace_concept`
    - :ref:`paperspace_concept`
    - :ref:`block_concept`

    **Classes:**

    - :class:`ezdxf.layouts.BaseLayout` - parent of all layouts
    - :class:`ezdxf.layouts.Layout` - parent of modelspace & paperspace
    - :class:`ezdxf.layouts.Modelspace`
    - :class:`ezdxf.layouts.Paperspace`
    - :class:`ezdxf.layouts.BlockLayout`
    - :class:`ezdxf.layouts.Layouts` - layout manager (:attr:`Drawing.layouts` attribute)
    - :class:`ezdxf.sections.blocks.BlocksSection` - blocks manager (:attr:`Drawing.blocks` attribute)

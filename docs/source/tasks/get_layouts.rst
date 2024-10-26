.. _get_layouts:

Get Layouts and Blocks
======================

Layouts and blocks contain all the graphical entities likes LINE, CIRCLE and so on.

Get all paperspace and modelspace layout names in arbitrary order:

.. code-block::

    layout_names = doc.layout_names()

Get all paperspace and modelspace layout names in tab-order of CAD applications:

.. code-block::

    layout_names = doc.layout_names_in_taborder()

Modelspace
----------

Each DXF document has one and only one :ref:`modelspace_concept` layout.

The :meth:`~ezdxf.document.Drawing.modelspace` method of the :class:`~ezdxf.document.Drawing`
class returns the :class:`~ezdxf.layouts.Modelspace` object.

.. code-block::

    msp = doc.modelspace()

Paperspace Layouts
------------------

Each DXF document has one or more :ref:`paperspace_concept` layout. DXF R12 supports
only one paperspace layout.

Get the active (default) paperspace layout:

.. code-block::

    psp = doc.paperspace()

Get a paperspace layout by name:

.. code-block::

    psp = doc.paperspace("Layout0")

The `name` argument is the name shown in the tabs of CAD applications.

Block Layouts
-------------

:ref:`block_concept` are collections of DXF entities which can be placed multiple times
as block references in different layouts and other block definitions.


Iterate over all block definitions:

.. code-block::

    for block in doc.blocks:
        print(block.name)

Get block definition by name:

.. code-block::

    block = doc.blocks.get("MyBlock")
    if block is None:
        print("block not found.")

Count block references:

.. code-block::

    from ezdxf import blkrefs

    ...

    counter = blkrefs.BlockReferenceCounter(doc)

    count = counter.by_name("MyBlock")
    print(f"MyBlock is referenced {count} times."

Find unused (unreferenced) block definitions:

.. versionadded:: 1.3.5

.. code-block::

    from ezdxf import blkrefs

    ...

    for name in blkrefs.find_unreferenced_blocks(doc)
        block = doc.blocks.get(name)

.. seealso::

    **Tasks:**

    - :ref:`add_layouts`
    - :ref:`delete_layouts`
    - :ref:`add_blockrefs`
    - :ref:`delete_dxf_entities`

    **Tutorials:**

    - :ref:`tut_blocks`

    **Basics:**

    - :ref:`layout`
    - :ref:`modelspace_concept`
    - :ref:`paperspace_concept`
    - :ref:`block_concept`

    **Classes:**

    - :class:`ezdxf.layouts.Modelspace`
    - :class:`ezdxf.layouts.Paperspace`
    - :class:`ezdxf.layouts.BlockLayout`
    - :class:`ezdxf.sections.blocks.BlocksSection`
    - :class:`ezdxf.document.Drawing`

    **Modules:**

    - :mod:`ezdxf.blkrefs`


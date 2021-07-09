.. module:: ezdxf.addons.dxf2code

.. _dxf2code:

dxf2code
========

Translate DXF entities and structures into Python source code.

Short example:

.. code-block:: Python

    import ezdxf
    from ezdxf.addons.dxf2code import entities_to_code, block_to_code

    doc = ezdxf.readfile('original.dxf')
    msp = doc.modelspace()
    source = entities_to_code(msp)

    # create source code for a block definition
    block_source = block_to_code(doc.blocks['MyBlock'])

    # merge source code objects
    source.merge(block_source)

    with open('source.py', mode='wt') as f:
        f.write(source.import_str())
        f.write('\n\n')
        f.write(source.code_str())
        f.write('\n')


.. autofunction:: entities_to_code

.. autofunction:: block_to_code

.. autofunction:: table_entries_to_code

.. autofunction:: black

.. class:: Code

    Source code container.

    .. attribute:: code

        Source code line storage, store lines without line ending ``\\n``

    .. attribute:: imports

        source code line storage for global imports, store lines without line ending ``\\n``

    .. attribute:: layers

        Layers used by the generated source code, AutoCAD accepts layer names without a LAYER table entry.

    .. attribute:: linetypes

        Linetypes used by the generated source code, these linetypes require a TABLE entry or AutoCAD will crash.

    .. attribute:: styles

        Text styles used by the generated source code, these text styles require a TABLE entry or AutoCAD will crash.

    .. attribute:: dimstyles

        Dimension styles  used by the generated source code, these dimension styles require a TABLE entry or AutoCAD will crash.

    .. attribute:: blocks

        Blocks used by the generated source code, these blocks require a BLOCK definition in the BLOCKS section or AutoCAD will crash.

    .. automethod:: code_str

    .. automethod:: black_code_str

    .. automethod:: import_str

    .. automethod:: merge

    .. automethod:: add_import

    .. automethod:: add_line

    .. automethod:: add_lines



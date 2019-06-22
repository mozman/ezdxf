.. automodule:: ezdxf.addons.dxf2code

.. autofunction:: entities_to_code

.. autofunction:: block_to_code

.. autofunction:: table_entries_to_code

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

    .. automethod:: import_str

    .. automethod:: merge

    .. automethod:: add_import

    .. automethod:: add_line

    .. automethod:: add_lines



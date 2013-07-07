Import data from another DXF Drawing
====================================

First create an Importer object::

    import ezdxf

    source_drawing.ezdxf.readfile("Source_DXF_Drawing.dxf")
    target_drawing = ezdxf.new(dxfversion=source_drawing.dxfversion)
    importer = ezdxf.Importer(source_drawing, target_drawing)


.. function::Importer.__init__(source, target, strict_mode=True)

    :param source: source drawing of type ezdxf.Drawing()
    :param target: target drawing of type ezdxf.Drawing()
    :param bool strict_mode: import is only possible, if the drawings are compatible.

Now you can import DXF tables, like layer definitions and dimension style definitions or block definitions from the
blocks section or DXF entities from the modelspace.

Import Tables
-------------

.. function::Importer.import_tables(query='*', conflict='discard')

    Import all tables listed by the query string, '*' means all tables.
    Valid table names are 'layers', 'linetypes', 'appids', 'dimstyles', 'styles', 'ucs', 'views', 'viewports' and
    'block_records'.

.. function::Importer.import_table(name, query='*', conflict='discard')

    Import table entries from a specific table, the query string specifies the entries to import, '*' means all table entries.

    :param str conflict: 'discard' | 'replace'

    - 'discard': already existing entries will be preserved
    - 'replace': already existing entries will replaced by entries from the source drawing

Import Block Definition
-----------------------

.. function::Importer.import_blocks(query='*', conflict='discard')

    Import block definitions, the query string specifies the blocks to import, '*' means all blocks.

    :param str conflict: 'discard' | 'replace' | 'rename'

    - 'discard': already existing blocks will be preserved
    - 'replace': already existing blocks will replaced by blocks from the source drawing
    - 'rename': the imported block gets a new name, existing references in the source drawing will be resolved if possible.
      Block references in the modelspace will be resolved, if they are imported AFTER importing the block definitions.

Import Modelspace Entities
--------------------------

.. function::Importer.import_modelspace_entities(query='*')

    Import DXF entities from source modelspace to the target modelspace, select DXF types to import by the query string,
    '*' means all DXF types. If called AFTER the :func:`Importer.import_blocks` method, references to renamed blocks will
    be resolved.

Additional Methods
------------------

.. function::Importer.is_compatible()

.. function::Importer.import_all(table_conflict='discard', block_conflict='discard')
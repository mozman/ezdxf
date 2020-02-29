.. module:: ezdxf.addons.iterdxf
    :noindex:

iterdxf
=======

This add-on allows iterating over entities of the modelspace of really big (> 5GB) DXF files which do not fit into
memory by only loading one entity at the time.

The entities are regular :class:`~ezdxf.entities.DXFGraphic` objects with access to all supported DXF attributes,
this entities can be written to new DXF files created by the :meth:`IterDXF.export` method.
The new :meth:`~ezdxf.layouts.BaseLayout.add_foreign_entity` method allows also to add this entities to
new regular `ezdxf` drawings (except for the INSERT entity), but resources like linetype and style are removed,
only layer will be preserved but only with default attributes like color ``7`` and linetype ``CONTINUOUS``.

The following example shows how to split a big DXF files into several separated DXF files which contains
only LINE, TEXT or POLYLINE entities.

.. code-block:: Python

    from ezdxf.addons import iterdxf

    doc = iterdxf.opendxf('big.dxf')
    line_exporter = doc.export('line.dxf')
    text_exporter = doc.export('text.dxf')
    polyline_exporter = doc.export('polyline.dxf')
    try:
        for entity in doc.modelspace():
            if entity.dxftype() == 'LINE':
                line_exporter.write(entity)
            elif entity.dxftype() == 'TEXT':
                text_exporter.write(entity)
            elif entity.dxftype() == 'POLYLINE':
                polyline_exporter.write(entity)
    finally:
        line_exporter.close()
        text_exporter.close()
        polyline_exporter.close()
        doc.close()

Supported DXF types:


3DFACE, ARC, ATTDEF, ATTRIB, CIRCLE, DIMENSION, ELLIPSE, HATCH, HELIX, IMAGE, INSERT,
LEADER, LINE, LWPOLYLINE, MESH, MLEADER, MLINE, MTEXT, POINT, POLYLINE, RAY, SHAPE,
SOLID, SPLINE, TEXT, TRACE, VERTEX, WIPEOUT, XLINE

Transfer simple entities to another DXF document, this works for some supported entities, except for entities with
strong dependencies to the original document like INSERT look at :meth:`~ezdxf.layouts.BaseLayout.add_foreign_entity`
for all supported types:

.. code-block:: Python

    newdoc = ezdxf.new()
    msp = newdoc.modelspace()
    # line is an entity from a big source file
    msp.add_foreign_entity(line)
    # and so on ...
    msp.add_foreign_entity(lwpolyline)
    msp.add_foreign_entity(mesh)
    msp.add_foreign_entity(polyface)

Transfer MESH and POLYFACE (dxftype for POLYFACE and POLYMESH is POLYLINE!) entities into a new DXF document by
the :class:`MeshTransformer` class:

.. code-block:: Python

    from ezdxf.render import MeshTransformer

    # mesh is MESH from a big source file
    t = MeshTransformer.from_mesh(mesh)
    # create a new MESH entity from MeshTransformer
    t.render(msp)

    # polyface is POLYFACE from a big source file
    t = MeshTransformer.from_polyface(polyface)
    # create a new POLYMESH entity from MeshTransformer
    t.render_polyface(msp)


Another way to import entities from a big source file into new DXF documents is to split the big file into
smaller parts and use the :class:`~ezdxf.addons.importer.Importer` add-on for a more safe entity import.

.. autofunction:: opendxf(filename: str) -> IterDXF

.. autofunction:: modelspace(filename: str, types:Iterable[str]=None) -> Iterable[DXFGraphic]

.. autofunction:: single_pass_modelspace(stream: BinaryIO, types:Iterable[str]=None) -> Iterable[DXFGraphic]

.. class:: IterDXF

    .. automethod:: export(name: str) -> IterDXFWriter

    .. automethod:: modelspace(types: Iterable[str] = None) -> Iterable[DXFGraphic]

    .. automethod:: close


.. class:: IterDXFWriter

    .. automethod:: write(entity: DXFGraphic)

    .. automethod:: close


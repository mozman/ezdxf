.. module:: ezdxf.addons.iterdxf
    :noindex:

iterdxf
=======

This add-on allows iterating over entities of the modelspace of really big (> 5GB) DXF files which do not fit into
memory by only loading one entity at the time.

The entities are regular :class:`~ezdxf.entities.DXFGraphic` objects with access
to all supported DXF attributes, this entities can be written to new DXF files but not assigned to other DXF
documents. The following example shows how to split a big DXF files into several separated DXF files which contains
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


Transfer simple entities to another DXF document:

.. code-block:: Python

    newdoc = ezdxf.new()
    msp = newdoc.modelspace()
    # line is an entity from a big source file
    # cumbersome but required to not introduce invalid dependencies like undefined linetypes
    msp.add_line(start=line.dxf.start, end=line.dxf.end)
    # lwpolyline is an entity from a big source file
    msp.add_lwpolyline(points=lwpolyline.points())

Don't forget to copy extrusion and elevation values for entities with an defined :ref:`OCS`.

Transfer MESH and POLYFACE (dxftype for POLYFACE and POLYMESH is POLYLINE!) entities into a new DXF document:

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


IterDXF
-------

.. class:: IterDXF

    .. automethod:: export(name: str) -> IterDXFWriter

    .. automethod:: modelspace() -> Iterable[DXFGraphic]

    .. automethod:: close

IterDXFWriter
-------------

.. class:: IterDXFWriter

    .. automethod:: write(entity: DXFGraphic)

    .. automethod:: close


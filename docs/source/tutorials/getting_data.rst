.. _tut_getting_data:

Tutorial for Getting Data from DXF Files
========================================

In this tutorial I show you how to get data from an existing DXF drawing.

At first load the drawing::

    import ezdxf

    dwg = ezdxf.readfile("your_dxf_file.dxf")

To learn more about document management see: :ref:`dwgmanagement`

Layouts
-------

I use the term layout as synonym for an arbitrary entity space which can contain any DXF construction element like
LINE, CIRCLE, TEXT and so on. Every construction element has to reside in exact one layout.

There are three different layout types:

- model space: this is the common construction place
- paper space: used to to create printable drawings
- block: reusable elements, every block has its own entity space

A DXF drawing consist of exact one model space and at least of one paper space. The DXF12 standard has only one unnamed
paper space the later DXF standards can have more than one paper space and each paper space has a name.

Iterate DXF Entities of a Layout
--------------------------------

Iterate over all construction elements in the model space::

    modelspace = dwg.modelspace()
    for e in modelspace:
        if e.dxftype() == 'LINE':
            print("LINE on layer: %s\n" % e.dxf.layer)
            print("start point: %s\n" % e.dxf.start)
            print("end point: %s\n" % e.dxf.end)

All layout objects supports the standard Python iterator protocol and the `in` operator.

Access DXF Attributes of an Entity
----------------------------------

Check the type of an DXF entity by :meth:`e.dxftype`. The DXF type is always uppercase.
All DXF attributes of an entity are grouped in the namespace entity.dxf::

    e.dxf.layer  # layer of the entity as string
    e.dxf.color  # color of the entity as integer

See common DXF attributes:

- :ref:`Common DXF attributes for DXF R12`
- :ref:`Common DXF attributes for DXF R13 or later`

Getting a Paper Space
---------------------

::

    paperspace = dwg.layout('layout0')

Retrieves the paper space named ``layout0``, the usage of the layout object is the same as of the model space object.
In the DXF12 standard only one paper space is defined, therefore the paper space name in the method call
:meth:`dwg.layout` is ignored or can be left off.

Iterate all DXF Entities at Once
--------------------------------

Because the DXF entities of the model space and the entities of all paper spaces are stored in the ENTITIES section of
the DXF drawing, you can also iterate over all drawing elements at once, except the entities placed in the block
layouts::

    for e in dwg.entities:
        print("DXF Entity: %s\n" % e.dxftype())

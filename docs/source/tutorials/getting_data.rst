.. _tut_getting_data:

Tutorial for Getting Data from DXF Files
========================================

In this tutorial I show you how to get data from an existing DXF drawing.

At first load the drawing::

    import ezdxf

    dwg = ezdxf.readfile("your_dxf_file.dxf")


.. seealso::

    :ref:`dwgmanagement`

Layouts
-------

I use the term layout as synonym for an arbitrary entity space which can contain any DXF entity like
LINE, CIRCLE, TEXT and so on. Every DXF entity can only reside in exact one layout.

There are three different layout types:

- model space: this is the common construction space
- paper space: used to to create print layouts
- block: reusable elements, every block has its own entity space

A DXF drawing consist of exact one model space and at least of one paper space. The DXF12 standard has only one unnamed
paper space the later DXF versions support more than one paper space and each paper space has a name.

Iterate over DXF Entities of a Layout
-------------------------------------

Iterate over all DXF entities in model space. Although this is a possible way to retrieve DXF entities, I
would like to point out that `entity queries`_ are the better way.::

    # iterate over all entities in model space
    msp = dwg.modelspace()
    for e in msp:
        if e.dxftype() == 'LINE':
            print_entity(e)

    # entity query for all LINE entities in model space
    for e in msp.query('LINE'):
        print_entity(e)

    def print_entity(e):
        print("LINE on layer: %s" % (e.dxf.layer,))
        print("start point: %s" % (e.dxf.start,))
        print("end point: %s\n" % (e.dxf.end,))

All layout objects supports the standard Python iterator protocol and the `in` operator.

Access DXF Attributes of an Entity
----------------------------------

Check the type of an DXF entity by :meth:`e.dxftype`. The DXF type is always uppercase.
All DXF attributes of an entity are grouped in the namespace :attr:`e.dxf`::

    e.dxf.layer  # layer of the entity as string
    e.dxf.color  # color of the entity as integer

See common DXF attributes:

- :ref:`Common DXF attributes for DXF R12`
- :ref:`Common DXF attributes for DXF R13 or later`

If a DXF attribute is not set (a valid DXF attribute has no value), a `ValueError` will be raised. To avoid this use
the :meth:`GraphicEntity.get_dxf_attrib` method with a default value::

    p = e.get_dxf_attrib('paperspace', 0)  # if 'paperspace' is left off, the entity defaults to model space

An unsupported DXF attribute raises an `AttributeError`.


Getting a Paper Space
---------------------

.. code::

    paperspace = dwg.layout('layout0')

Retrieves the paper space named ``layout0``, the usage of the layout object is the same as of the model space object.
The DXF12 standard provides only one paper space, therefore the paper space name in the method call
`dwg.layout('layout0')` is ignored or can be left off. For the later standards you get a list of the names of the
available layouts by :meth:`Drawing.layout_names`.

.. _entity queries:

Retrieve Entities by Query Language
-----------------------------------

Inspired by the wonderful `jQuery <http://www.jquery.com>`_ framework, I created a flexible query language for DXF
entities. To start a query use the :meth:`Layout.query` method, provided by all sort of layouts or use the
:meth:`ezdxf.query.new` function.

The query string is the combination of two queries, first the required entity query and second the optional attribute
query, enclosed in square brackets: ``'EntityQuery[AttributeQuery]'``

The entity query is a whitespace separated list of DXF entity names or the special name ``*``.
Where ``*`` means all DXF entities, all other DXF names have to be uppercase. The attribute query is used to select DXF
entities by its DXF attributes. The attribute query is an addition to the entity query and matches only if the
entity already match the entity query. The attribute query is a boolean expression, supported operators: ``and``,
``or``, ``!``.

.. seealso::

    :ref:`entity query string`

Get all `LINE` entities from the model space::

    modelspace = dwg.modelspace()
    lines = modelspace.query('LINE')

The result container also provides the `query()` method, get all LINE entities at layer ``construction``::

    construction_lines = lines.query('*[layer=="construction"]')

The ``*`` is a wildcard for all DXF entities, in this case you could also use ``LINE`` instead of ``*``, ``*`` works
here because `lines` just contains entities of DXF type LINE.

All together as one query::

    lines = modelspace.query('LINE[layer=="construction"]')

The ENTITIES section also supports the `query()` method::

    all_lines_and_circles_at_the_construction_layer = dwg.entities.query('LINE CIRCLE[layer=="construction"]')

Get all model space entities at layer ``construction``, but no entities with the `linestyle` ``DASHED``::

    not_dashed_entities = modelspace.query('*[layer=="construction" and linestyle!="DASHED"]')


.. _groupby:

Retrieve Entities by groupby
----------------------------

TODO

Default Layer Settings
----------------------

.. seealso::

    :ref:`tut_layers` and class :class:`Layer`


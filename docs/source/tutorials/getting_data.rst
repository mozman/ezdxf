.. _tut_getting_data:

Tutorial for Getting Data from DXF Files
========================================

In this tutorial I show you how to get data from an existing DXF drawing.

At first load the DXF drawing:

.. code-block:: Python

    import ezdxf

    doc = ezdxf.readfile("your_dxf_file.dxf")


.. seealso::

    :ref:`dwgmanagement`

Layouts
-------

I use the term layout as synonym for an arbitrary entity space which can contain DXF entities like LINE, CIRCLE, TEXT
and so on. Every DXF entity can only reside in exact one layout.

There are three different layout types:

- :class:`~ezdxf.layouts.Modelspace`: this is the common construction space
- :class:`~ezdxf.layouts.Paperspace`: used to to create print layouts
- :class:`~ezdxf.layouts.BlockLayout`: reusable elements, every block has its own entity space

A DXF drawing consist of exact one modelspace and at least of one paperspace. DXF R12 has only one unnamed
paperspace the later DXF versions support more than one paperspace and each paperspace has a name.

Iterate over DXF Entities of a Layout
-------------------------------------

Iterate over all DXF entities in modelspace. Although this is a possible way to retrieve DXF entities, I
would like to point out that `entity queries`_ are the better way.

.. code-block:: Python

    # iterate over all entities in modelspace
    msp = doc.modelspace()
    for e in msp:
        if e.dxftype() == 'LINE':
            print_entity(e)

    # entity query for all LINE entities in modelspace
    for e in msp.query('LINE'):
        print_entity(e)

    def print_entity(e):
        print("LINE on layer: %s\n" % e.dxf.layer)
        print("start point: %s\n" % e.dxf.start)
        print("end point: %s\n" % e.dxf.end)

All layout objects supports the standard Python iterator protocol and the ``in`` operator.

Access DXF Attributes of an Entity
----------------------------------

Check the type of an DXF entity by :meth:`e.dxftype`. The DXF type is always uppercase.
All DXF attributes of an entity are grouped in the namespace attribute :attr:`~ezdxf.entities.dxfentity.DXFEntity.dxf`:

.. code-block:: Python

    e.dxf.layer  # layer of the entity as string
    e.dxf.color  # color of the entity as integer

See :ref:`Common graphical DXF attributes`


If a DXF attribute is not set (a valid DXF attribute has no value), a :class:`DXFValueError` will be raised. To avoid this use
the :meth:`~ezdxf.entities.dxfentity.DXFEntity.get_dxf_attrib` method with a default value:

.. code-block:: Python

    # if DXF attribute 'paperspace' does not exist, the entity defaults to modelspace
    p = e.get_dxf_attrib('paperspace', 0)

An unsupported DXF attribute raises an :class:`DXFAttributeError`.


Getting a Paperspace Layout
---------------------------

.. code:: Python

    paperspace = doc.layout('layout0')

Retrieves the paperspace named ``layout0``, the usage of the :class:`~ezdxf.layouts.Layout` object is the same as of
the modelspace object. DXF R12 provides only one paperspace, therefore the paperspace name in the method call
:code:`doc.layout('layout0')` is ignored or can be left off. For the later DXF versions you get a list of the names
of the available layouts by :meth:`~ezdxf.drawing.Drawing.layout_names`.

.. _entity queries:

Retrieve Entities by Query Language
-----------------------------------

Inspired by the `jQuery <http://www.jquery.com>`_ framework, I created a flexible query language for DXF
entities. To start a query use the :meth:`~ezdxf.layouts.Layout.query` method, provided by all sort of layouts or use
the :meth:`ezdxf.query.new` function.

The query string is the combination of two queries, first the required entity query and second the optional attribute
query, enclosed in square brackets: ``'EntityQuery[AttributeQuery]'``

The entity query is a whitespace separated list of DXF entity names or the special name ``*``.
Where ``*`` means all DXF entities, all other DXF names have to be uppercase. The attribute query is used to select DXF
entities by its DXF attributes. The attribute query is an addition to the entity query and matches only if the
entity already match the entity query. The attribute query is a boolean expression, supported operators: ``and``,
``or``, ``!``.

.. seealso::

    :ref:`entity query string`

Get all LINE entities from the modelspace:

.. code-block:: Python

    modelspace = doc.modelspace()
    lines = modelspace.query('LINE')

The result container also provides the :meth:`query()` method, get all LINE entities at layer ``construction``:

.. code-block:: Python

    construction_lines = lines.query('*[layer=="construction"]')

The ``*`` is a wildcard for all DXF types, in this case you could also use ``LINE`` instead of ``*``, ``*`` works
here because ``lines`` just contains entities of DXF type LINE.

All together as one query:

.. code-block:: Python

    lines = modelspace.query('LINE[layer=="construction"]')

The ENTITIES section also supports the :meth:`query` method:

.. code-block:: Python

    all_lines_and_circles_at_the_construction_layer = doc.entities.query('LINE CIRCLE[layer=="construction"]')

Get all modelspace entities at layer ``construction``, but no entities with the `linestyle` ``DASHED``:

.. code-block:: Python

    not_dashed_entities = modelspace.query('*[layer=="construction" and linestyle!="DASHED"]')


.. _groupby:

Retrieve Entities by groupby
----------------------------

TODO

Default Layer Settings
----------------------

.. seealso::

    :ref:`tut_layers` and class :class:`~ezdxf.entities.layer.Layer`


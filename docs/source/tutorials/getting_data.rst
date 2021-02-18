.. _tut_getting_data:

Tutorial for getting data from DXF files
========================================

In this tutorial I show you how to get data from an existing DXF drawing.

Loading the DXF file:

.. code-block:: Python

    import sys
    import ezdxf

    try:
        doc = ezdxf.readfile("your_dxf_file.dxf")
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file.')
        sys.exit(2)

This works well with DXF files from trusted sources like AutoCAD or BricsCAD,
for loading DXF files with minor or major flaws look at the
:mod:`ezdxf.recover` module.

.. seealso::

    :ref:`dwgmanagement`

Layouts
-------

I use the term layout as synonym for an arbitrary entity space which can contain
DXF entities like LINE, CIRCLE, TEXT and so on. Every DXF entity can only reside
in exact one layout.

There are three different layout types:

- :class:`~ezdxf.layouts.Modelspace`: this is the common construction space
- :class:`~ezdxf.layouts.Paperspace`: used to to create print layouts
- :class:`~ezdxf.layouts.BlockLayout`: reusable elements, every block has its
  own entity space

A DXF drawing consist of exact one modelspace and at least of one paperspace.
DXF R12 has only one unnamed paperspace the later DXF versions support more than
one paperspace and each paperspace has a name.

Iterate over DXF entities of a layout
-------------------------------------

Iterate over all DXF entities in modelspace. Although this is a possible way to
retrieve DXF entities, I would like to point out that `entity queries`_ are the
better way.

.. code-block:: Python

    # helper function
    def print_entity(e):
        print("LINE on layer: %s\n" % e.dxf.layer)
        print("start point: %s\n" % e.dxf.start)
        print("end point: %s\n" % e.dxf.end)

    # iterate over all entities in modelspace
    msp = doc.modelspace()
    for e in msp:
        if e.dxftype() == 'LINE':
            print_entity(e)

    # entity query for all LINE entities in modelspace
    for e in msp.query('LINE'):
        print_entity(e)


All layout objects supports the standard Python iterator protocol and the
``in`` operator.

Access DXF attributes of an entity
----------------------------------

Check the type of an DXF entity by :meth:`e.dxftype`. The DXF type is always
uppercase. All DXF attributes of an entity are grouped in the namespace
attribute :attr:`~ezdxf.entities.dxfentity.DXFEntity.dxf`:

.. code-block:: Python

    e.dxf.layer  # layer of the entity as string
    e.dxf.color  # color of the entity as integer

See :ref:`Common graphical DXF attributes`


If a DXF attribute is not set (a valid DXF attribute has no value), a
:class:`DXFValueError` will be raised. To avoid this use the
:meth:`~ezdxf.entities.dxfentity.DXFEntity.get_dxf_attrib` method with a
default value:

.. code-block:: Python

    # If DXF attribute 'paperspace' does not exist, the entity defaults
    # to modelspace:
    p = e.get_dxf_attrib('paperspace', 0)

An unsupported DXF attribute raises an :class:`DXFAttributeError`.


Getting a paperspace layout
---------------------------

.. code:: Python

    paperspace = doc.layout('layout0')

Retrieves the paperspace named ``layout0``, the usage of the
:class:`~ezdxf.layouts.Layout` object is the same as of the modelspace object.
DXF R12 provides only one paperspace, therefore the paperspace name in the
method call :code:`doc.layout('layout0')` is ignored or can be left off.
For the later DXF versions you get a list of the names of the available
layouts by :meth:`~ezdxf.document.Drawing.layout_names`.

.. _entity queries:

Retrieve entities by query language
-----------------------------------

`ezdxf` provides a flexible query language for DXF entities.
All layout types have a :meth:`~ezdxf.layouts.BaseLayout.query` method to start
an entity query or use the :meth:`ezdxf.query.new` function.

The query string is the combination of two queries, first the required entity
query and second the optional attribute query, enclosed in square brackets:
``'EntityQuery[AttributeQuery]'``

The entity query is a whitespace separated list of DXF entity names or the
special name ``*``. Where ``*`` means all DXF entities, all other DXF names
have to be uppercase. The ``*`` search can exclude entity types by adding the
entity name with a presceding ``!`` (e.g. ``* !LINE``, search all entities except lines).

The attribute query is used to select DXF entities by its DXF attributes. The
attribute query is an addition to the entity query and matches only if the
entity already match the entity query. The attribute query is a
boolean expression, supported operators: ``and``, ``or``, ``!``.

.. seealso::

    :ref:`entity query string`

Get all LINE entities from the modelspace:

.. code-block:: Python

    msp = doc.modelspace()
    lines = msp.query('LINE')

The result container :class:`~ezdxf.query.EntityQuery` also provides the
:meth:`query()` method, get all LINE entities at layer ``construction``:

.. code-block:: Python

    construction_lines = lines.query('*[layer=="construction"]')

The ``*`` is a wildcard for all DXF types, in this case you could also use
``LINE`` instead of ``*``, ``*`` works here because ``lines`` just contains
entities of DXF type LINE.

All together as one query:

.. code-block:: Python

    lines = msp.query('LINE[layer=="construction"]')

The ENTITIES section also supports the :meth:`query` method:

.. code-block:: Python

    lines_and_circles = doc.entities.query('LINE CIRCLE[layer=="construction"]')

Get all modelspace entities at layer ``construction``, but excluding entities
with linetype ``DASHED``:

.. code-block:: Python

    not_dashed_entities = msp.query('*[layer=="construction" and linetype!="DASHED"]')


.. _using_groupby:

Retrieve entities by groupby() function
---------------------------------------

Search and group entities by a user defined criteria. As example let's group
all entities from modelspace by layer, the result will be a dict with layer
names as dict-key and a list of all entities from modelspace matching this layer
as dict-value. Usage as dedicated function call:

.. code-block:: Python

    from ezdxf.groupby import groupby
    group = groupby(entities=msp, dxfattrib='layer')

The `entities` argument can be any container or generator which yields
:class:`~ezdxf.entities.DXFEntity` or inherited objects. Shorter and simpler
to use as method of :class:`~ezdxf.layouts.BaseLayout` (modelspace,
paperspace layouts, blocks) and query results as
:class:`~ezdxf.query.EntityQuery` objects:

.. code-block:: Python

    group = msp.groupby(dxfattrib='layer')

    for layer, entities in group.items():
        print(f'Layer "{layer}" contains following entities:')
        for entity in entities:
            print('    {}'.format(str(entity)))
        print('-'*40)

The previous example shows how to group entities by a single DXF attribute,
but it is also possible to group entities by a custom key, to do so create a
custom key function, which accepts a DXF entity as argument and returns a
hashable value as dict-key or ``None`` to exclude the entity.
The following example shows how to group entities by layer and color, so
each result entry has a tuple ``(layer, color)`` as key and a list of entities
with matching DXF attributes:

.. code-block:: Python

    def layer_and_color_key(entity):
        # return None to exclude entities from result container
        if entity.dxf.layer == '0':  # exclude entities from default layer '0'
            return None
        else:
            return entity.dxf.layer, entity.dxf.color

    group = msp.groupby(key=layer_and_color_key)
    for key, entities in group.items():
        print(f'Grouping criteria "{key}" matches following entities:')
        for entity in entities:
            print('    {}'.format(str(entity)))
        print('-'*40)

To exclude entities from the result container the `key` function should return
``None``. The :func:`~ezdxf.groupby.groupby` function catches
:class:`DXFAttributeError` exceptions while processing entities and
excludes this entities from the result container. So there is no need to worry
about DXF entities which do not support certain attributes, they will be
excluded automatically.

.. seealso::

    :func:`~ezdxf.groupby.groupby` documentation


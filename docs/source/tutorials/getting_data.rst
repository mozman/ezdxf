.. _tut_getting_data:

Tutorial for getting data from DXF files
========================================

In this tutorial shows how to get data from an existing DXF document.
If you are a new `ezdxf` user, read also the tutorial :ref:`arch-usr`.

Loading the DXF file:

.. code-block:: Python

    import sys
    import ezdxf

    try:
        doc = ezdxf.readfile("your_dxf_file.dxf")
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
        sys.exit(2)

This works well for DXF files from trusted sources like AutoCAD or BricsCAD,
for loading DXF files with minor or major flaws look at the
:mod:`ezdxf.recover` module.

.. seealso::

    - :ref:`dwgmanagement`
    - :ref:`arch-usr`

Layouts
-------

The term layout is used as a synonym for an arbitrary entity space which can contain
DXF entities like LINE, CIRCLE, TEXT and so on. Each DXF entity can only reside
in exact one layout.

There are three different layout types:

- :class:`~ezdxf.layouts.Modelspace`: this is the common construction space
- :class:`~ezdxf.layouts.Paperspace`: used to to create print layouts
- :class:`~ezdxf.layouts.BlockLayout`: reusable elements, every block has its
  own entity space

A DXF document consist of exact one modelspace and at least one paperspace.
DXF R12 has only one unnamed paperspace the later DXF versions support more than
one paperspace and each paperspace has a name.

Getting the modelspace layout
-----------------------------

The modelspace contains the "real" world representation of the drawing subjects
in real world units. The modelspace has the fixed name "Model" and the DXF document
has a special getter method :meth:`~ezdxf.document.Drawing.modelspace`.

.. code:: Python

    msp = doc.modelspace()

Iterate over DXF entities of a layout
-------------------------------------

This code shows how to iterate over all DXF entities in modelspace:

.. code-block:: Python

    # helper function
    def print_entity(e):
        print("LINE on layer: %s\n" % e.dxf.layer)
        print("start point: %s\n" % e.dxf.start)
        print("end point: %s\n" % e.dxf.end)

    # iterate over all entities in modelspace
    msp = doc.modelspace()
    for e in msp:
        if e.dxftype() == "LINE":
            print_entity(e)

    # entity query for all LINE entities in modelspace
    for e in msp.query("LINE"):
        print_entity(e)


All layout objects supports the standard Python iterator protocol and the
``in`` operator.

Access DXF attributes of an entity
----------------------------------

The :meth:`e.dxftype` method returns the DXF type, the DXF type is always an
uppercase string like ``"LINE"``. All DXF attributes of an entity are grouped in
the namespace attribute :attr:`~ezdxf.entities.dxfentity.DXFEntity.dxf`:

.. code-block:: Python

    e.dxf.layer  # layer of the entity as string
    e.dxf.color  # color of the entity as integer

See :ref:`Common graphical DXF attributes`


If a DXF attribute is not set (the DXF attribute does not exist), a
:class:`DXFValueError` will be raised. The :meth:`get` method returns a default
value in this case or ``None`` if no default value is specified:

.. code-block:: Python

    # If DXF attribute 'paperspace' does not exist, the entity defaults
    # to modelspace:
    p = e.dxf.get("paperspace", 0)

or check beforehand if the attribute exist:

.. code-block:: Python

    if e.dxf.hasattr("paperspace"):
        ...

An unsupported DXF attribute raises a :class:`DXFAttributeError`, to check if
an attribute is supported by an entity use:

.. code-block:: Python

    if e.dxf.is_supported("paperspace"):
        ...

Getting a paperspace layout
---------------------------

.. code:: Python

    paperspace = doc.layout("layout0")

Retrieves the paperspace named ``layout0``, the usage of the
:class:`~ezdxf.layouts.Layout` object is the same as of the modelspace object.
DXF R12 provides only one paperspace, therefore the paperspace name in the
method call :code:`doc.layout("layout0")` is ignored or can be left off.
For newer DXF versions you can get a list of the available layout names
by the methods :meth:`~ezdxf.document.Drawing.layout_names` and
:meth:`~ezdxf.document.Drawing.layout_names_in_taborder`.

The method :meth:`~ezdxf.document.Drawing.paperspace` works in a similar way,
but has the proper return type annotation :class:`Paperspace`, which is
better for type checking:

.. code:: Python

    paperspace = doc.paperspace("layout0")

.. _entity queries:

Retrieve entities by query language
-----------------------------------

`Ezdxf` provides a flexible query language for DXF entities.
All layout types have a :meth:`~ezdxf.layouts.BaseLayout.query` method to start
an entity query or use the :meth:`ezdxf.query.new` function.

The query string is the combination of two queries, first the required entity
query and second the optional attribute query, enclosed in square brackets:
``"EntityQuery[AttributeQuery]"``

The entity query is a whitespace separated list of DXF entity names or the
special name ``*``. Where ``*`` means all DXF entities, all other DXF names
have to be uppercase. The ``*`` search can exclude entity types by adding the
entity name with a preceding ``!`` (e.g. ``* !LINE``, search all entities except
lines).

The attribute query is used to select DXF entities by its DXF attributes. The
attribute query is an addition to the entity query and matches only if the
entity already match the entity query. The attribute query is a
boolean expression, supported operators: ``and``, ``or``, ``!``.

.. seealso::

    :ref:`entity query string`

Get all LINE entities from the modelspace:

.. code-block:: Python

    msp = doc.modelspace()
    lines = msp.query("LINE")

The result container :class:`~ezdxf.query.EntityQuery` also provides the
:meth:`query()` method, get all LINE entities at layer ``construction``:

.. code-block:: Python

    construction_lines = lines.query('*[layer=="construction"]')

The ``*`` is a wildcard for all DXF types, in this case you could also use
``LINE`` instead of ``*``, ``*`` works here because ``lines`` just contains
LINE entities.

All together as one query:

.. code-block:: Python

    lines = msp.query('LINE[layer=="construction"]')

Get all modelspace entities at layer ``construction``, but excluding entities
with linetype ``DASHED``:

.. code-block:: Python

    not_dashed_entities = msp.query('*[layer=="construction" and linetype!="DASHED"]')

Extended EntityQuery Features
-----------------------------

Same task as above but using the extended query features of the
:class:`~ezdxf.query.EntityQuery` container:

.. code-block:: Python

    lines = msp.query("LINES").layer == "construction"
    not_dashed_lines = lines.linetype != "DASHED"

.. seealso::

    :ref:`extended query features`

.. _using_groupby:

Retrieve entities by groupby() function
---------------------------------------

Search and group entities by a user defined criteria. As example let's group
all entities from modelspace by layer, the result will be a dict with layer
names as dict-key and a list of all entities from modelspace matching this layer
as dict-value:

.. code-block:: Python

    from ezdxf.groupby import groupby
    group = groupby(entities=msp, dxfattrib="layer")

The `entities` argument can be any container or generator which yields
:class:`~ezdxf.entities.DXFEntity` or inherited objects. Shorter and simpler
to use as method of :class:`~ezdxf.layouts.BaseLayout` (modelspace,
paperspace layouts, blocks) and query results as
:class:`~ezdxf.query.EntityQuery` objects:

.. code-block:: Python

    group = msp.groupby(dxfattrib="layer")

    for layer, entities in group.items():
        print(f'Layer "{layer}" contains following entities:')
        for entity in entities:
            print(f"    {entity}")
        print("-"*40)

The previous example shows how to group entities by a single DXF attribute,
but it's also possible to group entities by a custom key, to do so create a
custom key function, which accepts a DXF entity as argument and returns a
hashable value as dict-key or ``None`` to exclude the entity.
The following example shows how to group entities by layer and color, so
each result entry has a tuple ``(layer, color)`` as key and a list of entities
with matching DXF attributes as values:

.. code-block:: Python

    def layer_and_color_key(entity):
        # return None to exclude entities from result container
        if entity.dxf.layer == "0":  # exclude entities from default layer "0"
            return None
        else:
            return entity.dxf.layer, entity.dxf.color

    group = msp.groupby(key=layer_and_color_key)
    for key, entities in group.items():
        print(f'Grouping criteria "{key}" matches following entities:')
        for entity in entities:
            print(f"    {entity}")
        print("-"*40)

The :func:`~ezdxf.groupby.groupby` function catches :class:`DXFAttributeError`
exceptions while processing entities and excludes this entities from the result.
So there is no need to worry about DXF entities which do not support certain
attributes, they will be excluded automatically.

.. seealso::

    :func:`~ezdxf.groupby.groupby` documentation


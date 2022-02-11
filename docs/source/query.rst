.. module:: ezdxf.query

.. seealso::

    For usage of the query features see the tutorial: :ref:`tut_getting_data`

.. _entity query string:

Entity Query String
===================

::

    QueryString := EntityQuery ("[" AttribQuery "]" "i"?)*

The query string is the combination of two queries, first the required entity query and second the
*optional* attribute query, enclosed in square brackets, append ``'i'`` after the closing square bracket
to ignore case for strings.

Entity Query
------------

The entity query is a whitespace separated list of DXF entity names or the special name ``'*'``.
Where ``'*'`` means all DXF entities, exclude some entity types by appending their names with a preceding ``!``
(e.g. all entities except LINE = ``'* !LINE'``). All DXF names have to be uppercase.

Attribute Query
---------------

The *optional* attribute query is a boolean expression, supported operators are:

  - not (!): !term is true, if term is false
  - and (&): term & term is true, if both terms are true
  - or (|): term | term is true, if one term is true
  - and arbitrary nested round brackets
  - append (i) after the closing square bracket to ignore case for strings

Attribute selection is a term: "name comparator value", where name is a DXF entity attribute in lowercase,
value is a integer, float or double quoted string, valid comparators are:

  - ``"=="`` equal "value"
  - ``"!="`` not equal "value"
  - ``"<"`` lower than "value"
  - ``"<="`` lower or equal than "value"
  - ``">"`` greater than "value"
  - ``">="`` greater or equal than "value"
  - ``"?"`` match regular expression "value"
  - ``"!?"`` does not match regular expression "value"

.. _query result:

Query Result
------------

The :class:`EntityQuery` class is the return type of all :meth:`query` methods.
:class:`EntityQuery` contains all DXF entities of the source collection,
which matches one name of the entity query AND the whole attribute query.
If a DXF entity does not have or support a required attribute, the corresponding attribute search term is ``False``.

examples:

    - :code:`LINE[text ? ".*"]`: always empty, because the LINE entity has no text attribute.
    - :code:`LINE CIRCLE[layer=="construction"]`: all LINE and CIRCLE entities with layer  == ``"construction"``
    - :code:`*[!(layer=="construction" & color<7)]`: all entities except those with layer  == ``"construction"`` and color < ``7``
    - :code:`*[layer=="construction"]i`, (ignore case) all entities with layer == ``"construction"`` | ``"Construction"`` | ``"ConStruction"`` ...

EntityQuery Class
=================

.. class:: EntityQuery

    The :class:`EntityQuery` class is a result container, which is filled with dxf entities matching the query string.
    It is possible to add entities to the container (extend), remove entities from the container and
    to filter the container. Supports the standard `Python Sequence`_ methods and protocols.

    .. autoattribute:: first

    .. autoattribute:: last

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: __iter__

    .. automethod:: extend

    .. automethod:: remove

    .. automethod:: query

    .. automethod:: groupby

Extended EntityQuery Features
-----------------------------

.. versionadded:: 0.18

The ``[]`` operator got extended features in version 0.18, until then the
:class:`EntityQuery` implemented the :meth:`__getitem__` interface like a
sequence to get entities from the container:

.. code-block:: Python

    result = msp.query(...)
    first = result[0]
    last = result[-1]
    sequence = result[1:-2]  # returns not an EntityQuery container!

Now the :meth:`__getitem__` function accepts an DXF attribute name and returns
all entities which support this attribute, this is the base for supporting
queries by relation operators. More on that later.

The :meth:`__setitem__` method the assigns a DXF attribute all supported
entities in the :class:`EntityQuery` container:

.. code-block:: Python

    result = msp.query(...)
    result["layer"] = "MyLayer"

Entities which do not support an attribute are silently ignored:

.. code-block:: Python

    result = msp.query(...)
    result["center"] = (0, 0)  # set center only of CIRCLE and ARC entities

The :meth:`__delitem__` method discards DXF attributes from all entities in
the :class:`EntityQuery` container:

.. code-block:: Python

    result = msp.query(...)
    # reset the layer attribute from all entities in container result to the
    # default layer "0"
    del result["layer"]

Selection by Relation Operators
-------------------------------

.. versionadded:: 0.18

The attribute selection by :meth:`__getitem__` allows further selections by
comparison operators:

.. code-block:: Python

    msp.add_line((0, 0), (1, 0), dxfattribs={"layer": "MyLayer})
    lines = msp.query("LINE")
    # select all entities on layer "MyLayer"
    entities = lines["layer"] == "MyLayer"
    assert len(entities) == 1

    # or select all except the entities on layer "MyLayer"
    entities = lines["layer"] != "MyLayer"

The selection by operator is case insensitive by default, because all DXF table
entries are handled case insensitive. But if required the selection mode can
be set to case sensitive:

.. code-block:: Python

    lines = msp.query("LINE")
    # use case sensitive selection: "MyLayer" != "MYLAYER"
    lines.case_insensitive = False
    entities = lines["layer"] == "MYLAYER"
    assert len(entities) == 0

    # the entities container has the default setting:
    assert entities.case_insensitive is True

The new() Function
------------------

.. autofunction:: ezdxf.query.new(entities: Iterable['DXFEntity'] = None, query: str = '*') -> EntityQuery

.. _Python Sequence: http://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence



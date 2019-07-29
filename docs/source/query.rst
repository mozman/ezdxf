.. _name query string:

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

examples::

    'LINE[text ? ".*"]' is always empty, because the LINE entity has no text attribute.

    'LINE CIRCLE[layer=="construction"]' => all LINE and CIRCLE entities on layer "construction"
    '*[!(layer=="construction" & color<7)]' => all entities except those on layer == "construction" and color < 7
    '*[layer=="construction"]i' => (ignore case) all entities with layer == "construction" | "Construction" | "ConStruction" ...

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

    .. automethod:: __iter__

    .. automethod:: extend

    .. automethod:: remove

    .. automethod:: query

    .. automethod:: groupby


The new() Function
------------------

.. automethod:: ezdxf.query.new(entities: Iterable['DXFEntity'] = None, query: str = '*') -> EntityQuery

.. _Python Sequence: http://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence
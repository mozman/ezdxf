.. _name query string:

Name Query String
=================

A name query string is just a standard regular expression see: http://docs.python.org/3/library/re.html

A ``'$'`` will be appended to the query string.

For general usage of the query features see the tutorial: :ref:`tut_getting_data`

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
If a DXF entity does not have or support a required attribute, the corresponding attribute search term is false.

examples::

    'LINE[text ? ".*"]' is always empty, because the LINE entity has no text attribute.

    'LINE CIRCLE[layer=="construction"]' => all LINE and CIRCLE entities on layer "construction"
    '*[!(layer=="construction" & color<7)]' => all entities except those on layer == "construction" and color < 7
    '*[layer=="construction"]i' => (ignore case) all entities with layer == "construction" | "Construction" | "ConStruction" ...

EntityQuery Class
=================

.. class:: EntityQuery(Sequence)

    The :class:`EntityQuery` class is a result container, which is filled with dxf entities matching the query string.
    It is possible to add entities to the container (extend), remove entities from the container and
    to filter the container. Supports the standard sequence methods and protocols.
    `(Python Sequence Docs) <http://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence>`_


.. attribute:: EntityQuery.first

    Returns first entity or `None`.

.. attribute:: EntityQuery.last

    Returns last entity or `None`.

.. method:: EntityQuery.__init__(entities, query='*')

   Setup container with entities matching the initial query.

   :param entities: sequence of wrapped DXF entities (at least :class:`GraphicEntity` class)
   :param str query: `entity query string`_


.. method:: EntityQuery.extend(entities, query='*', unique=True)

   Extent the query container by entities matching an additional query.

.. method:: EntityQuery.remove(query='*')

   Remove all entities from result container matching this additional query.

.. method:: EntityQuery.query(query='*')

   Returns a new result container with all entities matching this additional query.

.. method:: EntityQuery.groupby(dxfattrib='', key=None)

   Returns a mapping of this result container, where entities are grouped by a dxfattrib or a key function.

   :param str dxfattrib: grouping DXF attribute like 'layer'
   :param function key: key function, which accepts a DXFEntity as argument, returns grouping key of this entity or
       None for ignore this object. Reason for ignoring: a queried DXF attribute is not supported by this entity


The new() Function
------------------

.. method:: ezdxf.query.new(entities, query='*')

   Start a new query based on a sequence `entities`. The sequence `entities` has to provide the Python iterator
   protocol and has to yield at least subclasses of :class:`GenericWrapper` or better :class:`GraphicEntity`.
   Returns an object of type :class:`EntityQuery`.

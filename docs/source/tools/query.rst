.. reference - usage is documented in tasks - "Query data"

.. module:: ezdxf.query

Query Module
============

.. seealso::

    - :ref:`tut_getting_data`
    - Usage of extended query features: :ref:`query entities`

The new() Function
++++++++++++++++++

.. autofunction:: ezdxf.query.new

.. _entity query string:

Entity Query String
-------------------

.. code-block::

    QueryString := EntityQuery ("[" AttribQuery "]" "i"?)*

The query string is the combination of two queries, first the required entity query and 
second the optional attribute query, enclosed in square brackets, append ``'i'`` after 
the closing square bracket to ignore case for strings.

Entity Query
++++++++++++

The entity query is a whitespace separated list of DXF entity names or the special name 
``'*'``. Where ``'*'`` means all DXF entities, exclude some entity types by appending 
their names with a preceding ``!`` (e.g. all entities except LINE = ``'* !LINE'``). 
All DXF names have to be uppercase.

Attribute Query
+++++++++++++++

The *optional* attribute query is a boolean expression, supported operators are:

  - not (!): !term is true, if term is false
  - and (&): term & term is true, if both terms are true
  - or (|): term | term is true, if one term is true
  - and arbitrary nested round brackets
  - append (i) after the closing square bracket to ignore case for strings

Attribute selection is a term: "name comparator value", where name is a DXF
entity attribute in lowercase, value is a integer, float or double quoted string,
valid comparators are:

  - ``==`` equal "value"
  - ``!=`` not equal "value"
  - ``<`` lower than "value"
  - ``<=`` lower or equal than "value"
  - ``>`` greater than "value"
  - ``>=`` greater or equal than "value"
  - ``?`` match regular expression "value"
  - ``!?`` does not match regular expression "value"


EntityQuery Class
-----------------

.. class:: EntityQuery

    The :class:`EntityQuery` class is a result container, which is filled with DXF 
    entities matching the query string. It is possible to add entities to the container 
    (extend), remove entities from the container and to filter the container. 
    Supports the standard Python Sequence methods and protocols.  
    Does not remove automatically destroyed entities (entities deleted by calling method 
    :meth:`destroy`), the method :meth:`purge` has to be called explicitly to remove the 
    destroyed entities.

    .. autoattribute:: first

    .. autoattribute:: last

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: __eq__

    .. automethod:: __ne__

    .. automethod:: __lt__

    .. automethod:: __le__

    .. automethod:: __gt__

    .. automethod:: __ge__

    .. automethod:: match

    .. automethod:: __or__

    .. automethod:: __and__

    .. automethod:: __sub__

    .. automethod:: __xor__

    .. automethod:: __iter__

    .. automethod:: purge

    .. automethod:: extend

    .. automethod:: remove

    .. automethod:: query

    .. automethod:: groupby

    .. automethod:: filter

    .. automethod:: union

    .. automethod:: intersection

    .. automethod:: difference

    .. automethod:: symmetric_difference




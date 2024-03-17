.. Task section

.. module:: ezdxf.query
    :noindex:

.. _query entities:

Query Entities
==============

DXF entities can be selected from layouts or arbitrary entity-sequences based on their 
DXF type and attributes.  Create new queries be the :func:`new` function or by the 
:meth:`~ezdxf.layouts.BaseLayout.query` methods implemented by all layouts.

.. seealso::

    - Tutorial: :ref:`tut_getting_data`
    - Reference: :mod:`ezdxf.query` module

Entity Query String
-------------------

The query string is the combination of two queries, first the required entity query and 
second the optional attribute query, enclosed in square brackets, append ``'i'`` after 
the closing square bracket to ignore case for strings.


.. _query result:

Query Result
------------

The :class:`EntityQuery` class is the return type of all :meth:`query` methods.
:class:`EntityQuery` contains all DXF entities of the source collection,
which matches one name of the entity query AND the whole attribute query.
If a DXF entity does not have or support a required attribute, the corresponding
attribute search term is ``False``.

Select all LINE and CIRCLE entities with layer  == "construction"::

    result = msp.query('LINE CIRCLE[layer=="construction"]')

This result is always empty, because the LINE entity has no text attribute::

    result = msp.query('LINE[text ? ".*"]')

Select all entities except those with layer  == "construction" and color < 7::

    result = msp.query('*[!(layer=="construction" & color<7)]')

Ignore case, selects all entities with layer == "construction", "Construction", "ConStruction" ...::

    result = msp.query('*[layer=="construction"]i')

.. _extended query features:

Extended EntityQuery Features
-----------------------------

The :class:`EntityQuery` container supports the full Sequence protocol::

    result = msp.query(...)
    first = result[0]
    last = result[-1]

Slices return a new :class:`EntityQuery` container::

    sequence = result[1:-2]

The :meth:`__getitem__` function accepts also a DXF attribute name and returns all 
entities which support this attribute, this is the base for supporting queries by 
relational operators. More on that later.

The :meth:`__setitem__` method assigns a DXF attribute to all supported
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

Descriptors for DXF Attributes
------------------------------

For some basic DXF attributes exist descriptors in the :class:`EntityQuery` class:

- :attr:`layer`: layer name as string
- :attr:`color`: :ref:`ACI`, see :mod:`ezdxf.colors`
- :attr:`linetype`: linetype as string
- :attr:`ltscale`: linetype scaling factor as float value
- :attr:`lineweight`: :ref:`Lineweights`
- :attr:`invisible`: 0 if visible 1 if invisible, 0 is the default value
- :attr:`true_color`: true color as int value, see :mod:`ezdxf.colors`, has no default value
- :attr:`transparency`: transparency as int value, see :mod:`ezdxf.colors`, has no default value

A descriptor simplifies the attribute access through the :class:`EntityQuery`
container and has auto-completion support from IDEs:

.. code-block:: Python

    result = msp.query(...)
    # set attribute of all entities in result
    result.layer = "MyLayer"
    # delete attribute from all entities in result
    del result.layer
    # and for selector usage, see following section
    assert len(result.layer == "MyLayer") == 1

.. _relational selection operators:

Relational Selection Operators
------------------------------

The attribute selection by :meth:`__getitem__` allows further selections by
relational operators:

.. code-block:: Python

    msp.add_line((0, 0), (1, 0), dxfattribs={"layer": "MyLayer})
    lines = msp.query("LINE")
    # select all entities on layer "MyLayer"
    entities = lines["layer"] == "MyLayer"
    assert len(entities) == 1

    # or select all entities except the entities on layer "MyLayer"
    entities = lines["layer"] != "MyLayer"

These operators work only with real DXF attributes, for instance the :attr:`rgb`
attribute of graphical entities is not a real DXF attribute either the
:attr:`vertices` of the LWPOLYLINE entity.

The selection by relational operators is case insensitive by default, because
all names of DXF table entries are handled case insensitive. But if required
the selection mode can be set to case sensitive:

.. code-block:: Python

    lines = msp.query("LINE")
    # use case sensitive selection: "MyLayer" != "MYLAYER"
    lines.ignore_case = False
    entities = lines["layer"] == "MYLAYER"
    assert len(entities) == 0

    # the result container has the default setting:
    assert entities.ignore_case is True

Supported selection operators are:

  - ``==`` equal "value"
  - ``!=`` not equal "value"
  - ``<`` lower than "value"
  - ``<=`` lower or equal than "value"
  - ``>`` greater than "value"
  - ``>=`` greater or equal than "value"

The relational operators <, >, <= and >= are not supported for vector-based
attributes such as `center` or `insert` and raise a :class:`TypeError`.

.. note::

    These operators are selection operators and not logic operators, therefore
    the logic operators ``and``, ``or`` and ``not`` are **not** applicable.
    The methods :meth:`~EntityQuery.union`, :meth:`~EntityQuery.intersection`,
    :meth:`~EntityQuery.difference` and :meth:`~EntityQuery.symmetric_difference`
    can be used to combine selection. See section `Query Set Operators`_ and
    `Build Custom Filters`_.

.. _regular expression selection:

Regular Expression Selection
----------------------------

The :meth:`EntityQuery.match` method returns all entities where the selected DXF
attribute matches the given regular expression. This methods work only on string
based attributes, raises :class:`TypeError` otherwise.

From here on I use only descriptors for attribute selection if possible.

.. code-block:: Python

    msp.add_line((0, 0), (1, 0), dxfattribs={"layer": "Lay1"})
    msp.add_line((0, 0), (1, 0), dxfattribs={"layer": "Lay2"})
    lines = msp.query("LINE")

    # select all entities at layers starting with "Lay",
    # selection is also case insensitive by default:
    assert len(lines.layer.match("^Lay.*")) == 2

.. _build custom filters:

Build Custom Filters
--------------------

The method :class:`EntityQuery.filter` can be used to build operators for
none-DXF attributes or for complex logic expressions.

Find all MTEXT entities in modelspace containing "SearchText".
All :class:`~ezdxf.entities.MText` entities have a :attr:`text` attribute, no
need for a safety check:

.. code-block:: Python

    mtext = msp.query("MTEXT").filter(lambda e: "SearchText" in e.text)

This filter checks the non-DXF attribute :attr:`rgb`. The filter has to
check if the :attr:`rgb` attributes exist to avoid exceptions, because not all
entities in modelspace may have the :attr:`rgb` attribute e.g. the
:class:`DXFTagStorage` entities which preserve unknown DXF entities:

.. code-block:: Python

    result = msp.query().filter(
        lambda e: hasattr(e, "rgb") and e.rgb == (0, 0, 0)
    )

Build 1-pass logic filters for complex queries, which would require otherwise
multiple passes:

.. code-block:: Python

    result = msp.query().filter(lambda e: e.dxf.color < 7 and e.dxf.layer == "0")

Combine filters for more complex operations. The first filter passes only
valid entities and the second filter does the actual check:

.. code-block:: Python

    def validator(entity):
        return True  # if entity is valid and has all required attributes

    def check(entity):
        return True  # if entity passes the attribute checks

    result = msp.query().filter(validator).filter(check)

.. _query set operators:

Query Set Operators
-------------------

The ``|`` operator or :meth:`EntityQuery.union` returns a new
:class:`EntityQuery` with all entities from both queries. All entities are
unique - no duplicates. This operator acts like the logical ``or`` operator.

.. code-block:: Python

    entities = msp.query()
    # select all entities with color < 2 or color > 7
    result = (entities.color < 2 ) | (entities.color > 7)

The ``&`` operator or :meth:`EntityQuery.intersection` returns a new
:class:`EntityQuery` with entities common to `self` and `other`. This operator
acts like the logical ``and`` operator.

.. code-block:: Python

    entities = msp.query()
    # select all entities with color > 1 and color < 7
    result = (entities.color > 1) & (entities.color < 7)

The ``-`` operator or :meth:`EntityQuery.difference` returns a new
:class:`EntityQuery` with all entities from `self` that are not in `other`.

.. code-block:: Python

    entities = msp.query()
    # select all entities with color > 1 and not layer == "MyLayer"
    result = (entities.color > 1) - (entities.layer != "MyLayer")

The ``^`` operator or :meth:`EntityQuery.symmetric_difference` returns a new
:class:`EntityQuery` with entities in either `self` or `other` but not both.

.. code-block:: Python

    entities = msp.query()
    # select all entities with color > 1 or layer == "MyLayer", exclusive
    # entities with color > 1 and layer == "MyLayer"
    result = (entities.color > 1) ^ (entities.layer == "MyLayer")


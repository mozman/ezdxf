
.. module:: ezdxf.acis

.. ACIS_internals

ACIS Management Tool
====================

.. versionadded:: 0.18

These are low-level :term:`ACIS` data management tools for analyzing, parsing and
creating ACIS data structures.
These tools cannot replace the official :term:`ACIS` SDK due to the complexity of
the data structures and the absence of an :term:`ACIS` kernel. Without access to
the full documentation it is very cumbersome to reverse-engineer entities and
their properties, therefore the analysis of the :term:`ACIS` data structures is
limited to the use as embedded data in DXF and DWG files.

The `ezdxf` library does not provide an :term:`ACIS` kernel and there are no
plans for implementing one because this is far beyond my capabilities, but it
is possible to extract geometries made up only by planar polygonal faces and
maybe in the future it is also possible to create such polygon face meshes.

.. warning::

    Do not import from the implementation sub-package :mod:`ezdxf._acis`, always
    import from the API module :mod:`ezdxf.acis`.

Functions
=========

.. autofunction:: parse_sat(s: Union[str, Sequence[str]]) -> SatBuilder

.. autofunction:: body_to_mesh(body: RawEntity, merge_lumps=True) -> List[MeshTransformer]

.. autofunction:: body_planar_polygon_faces(body: RawEntity) -> Iterator[List[Sequence[Vec3]]]

.. autofunction:: lump_planar_polygon_faces(lump: RawEntity, m: Matrix44 = None) -> Iterator[Sequence[Vec3]]


Classes
=======

SatBuilder
----------

.. class:: SatBuilder

    Low level data structure to manage SAT data (Standard ACIS Text) files.

    .. attribute:: header

        :class:`AcisHeader`

    .. attribute:: entities

        List of all entities as :class:`SatEntity` instances managed by this
        builder.

    .. attribute:: bodies

        List of :class:`SatEntity` instances.
        The `body` entity is always the root entity for an ACIS geometry.

    .. automethod:: dump_sat

        Write the final SAT file:

        .. code-block:: Python

            lines = builder.dump_sat()
            with open("name.sat", "wt") as fp:
                fp.write("\n".join(lines))

    .. automethod:: query(func=lambda e: True) -> Iterator[SatEntity]

SatEntity
----------

.. class:: SatEntity

    Low level representation of an ACIS entity in SAT format.

    .. attribute:: name

        entity type

    .. attribute:: id

        Unique `id` as int or -1 for `id` not acquired. The ACIS data embedded
        in DXF files do not use ids, so the `id` in DXF files is always -1.

    .. attribute:: data

        Generic data container. References to other entities (pointers) are
        :class:`SatEntity` instances, the basic types `float` and `int` are
        still strings.

        Avoid accessing the :attr:`data` directly and use the
        :meth:`parse_values` method instead to acquire data from an
        entity.

    .. attribute:: attributes

        Reference to entity attributes or a ``NULL_PTR``.

    .. automethod:: find_all(entity_type: str) -> list[SatEntity]

    .. automethod:: find_first(entity_type: str) -> SatEntity

    .. automethod:: find_path(path: str) -> SatEntity

    .. automethod:: find_entities(names: str) -> list[SatEntity]

    .. automethod:: parse_values

AcisHeader
----------

.. class:: AcisHeader

    Represents an ACIS file header.

    .. attribute:: version

        ACIS version as int

    .. attribute:: acis_version

        ACIS version string

    .. attribute:: units_in_mm

        Count of millimeters which represent one drawing unit.

    .. method:: dumps() -> list(str)

        Returns the file header as list of strings.

    .. method:: set_version(version: int) -> None

        Sets the ACIS version as an integer value and updates the version
        string accordingly.



Exceptions
==========

.. class:: AcisException

    Base exception of the :mod:`acis` module.

.. class:: InvalidLinkStructure

.. class:: ParsingError

Entity Documentation
====================

A document (`sat.pdf`_) about the basic ACIS 7.0 file format is floating in the
internet.

This section contains the additional information about the entities,
I got from analyzing the SAT data extracted from DXF files exported
by BricsCAD.

This documentation ignores the differences to the ACIS format prior to 7.0.
The missing `id` is handled internally and missing entity references can often
be ignored if you use the flexible parsing methods of :class:`SatEntity`.
Writing support for SAT version < 7.0 is not required because all CAD
applications should be able to process version 7.0, even if embedded in a very
old DXF R2000 format (tested with Autodesk TrueView, BricsCAD and Nemetschek
Allplan).

The first goal is to document the entities which are required to represent
a geometry as polygonal faces (polygon face mesh), which can be converted into
a :class:`~ezdxf.render.MeshBuilder` object.

The entity data is described as stored in the :class:`SatEntity` class.
The entity type is stored in :attr:`~SatEntity.name`. The entity attributes
are stored as reference to an :class:`SatEntity` instance in
:attr:`~SatEntity.attributes` or the ``NULL_PTR`` instance if no attributes exist.
The :attr:`~SatEntity.id` is an integer value, but I have not seen any usage
of the id in DXF files, so it can always be -1.
The data fields are stored in the :attr:`~SatEntity.data` attribute, the
meaning of the data fields is the content of this section.
Each entry describes the fields starting after the `id` field
which is the 3rd record entry, as example the `transform`_ entity:

    transform $-1 -1 1 0 0 0 1 0 0 0 1 3.5 3.5 3.5 1 no_rotate no_reflect no_shear

The 1st field is the entity type `transform`_, the 2nd field is the attribute
pointer, "$-1" is the ``NULL_PTR`` and the 3rd field is an id of -1, the
documentation of `transform`_ starts at the 4th field.

Unknown data is listed as `<?>` for an unknown numeric value and `<~>`
for an unknown ``NULL_PTR``.

Data Types
----------

    - float values
    - integer values
    - constant strings like "forward" or "reversed"
    - user strings with a preceding length encoding like "@7 unknown"
    - pointers as record number with a preceding "$" like "$7" points to the
      7th record (0-based!) and "$-1" represents the ``NULL_PTR``

body
----

.. code-block:: text

    body <>attrib> <id> <~> <lump> <~> <transform>

Represents a solid geometry, which can consist of multiple `lump`_ entities.
The `transform`_ entity is an affine transformation operation.

coedge
------

.. code-block:: text

    coedge <attrib> ID <~> <coedge-0> <coedge-1> <coedge-2> <edge> reversed <loop> <~>

The coedges are a double linked list where `<coedge-0>` points to the next coedge
and `<coedge-1>` to the previous coedge. The `<coedge-2>` field points to the
partner coedge of the adjacent face.
In a closed surface each edge is part of two adjacent faces with opposite
orientations. The `<edge>` field points the geometric `edge`_
of the face. The `<loop>` field points to the parent `loop` entity.

edge
----

.. code-block:: text

    edge <attrib> ID <~> <vertex> <?0> <vertex> <?1> <coedge> <straight-curve> forward @7 unknown

face
----

.. code-block:: text

    face <attrib> ID <~> <face> <loop> <shell> <~> <plane-surface> forward single

loop
----

.. code-block:: text

    loop <attrib> ID <~> <~> <coedge> <face>

lump
----

.. code-block:: text

    lump <attrib> <id> <~> <lump> <shell> <body>

The lump represents a connected entity and there can be multiple lumps in a
`body`_. Multiple lumps are linked together by the `<lump>` field which
points to the next lump entity the last lump has a ``NULL_PTR`` as next pointer.
The `<body>` field points to the parent `body`_ entity.


plane-surface
-------------

.. code-block:: text

    plane-surface <attrib> ID <~> <x> <y> <z> <ux> <uy> <uz> <vx> <vy> <vz> forward_v I I I I

point
-----

.. code-block:: text

    point <attrib> <id> <~> <x> <y> <z>

Represents a point in space where `x`, `y` and `z` are the cartesian
coordinates as float values.

shell
-----

.. code-block:: text

    shell <attrib> ID ~ ~ ~ <face> ~ <lump>

straight-curve
--------------

.. code-block:: text

    straight-curve <attrib> ID <~> <x> <y> <z> <ux> <uy> <uz> I I

transform
---------

.. code-block:: text

    transform <attrib> <id> <a> <b> <c> <d> <e> <f> <g> <h> <i> <j> <k> <l> ...
        ... <?> no_rotate no_reflect no_shear

Example:

.. code-block:: text

    transform $-1 -1 1 0 0 0 1 0 0 0 1 3.5 3.5 3.5 1 no_rotate no_reflect no_shear

Represents a transformation matrix without the last column in terms of the
usage in :class:`ezdxf.math.Matrix44`::

    a b c 0 = 1   0   0   0
    d e f 0 = 0   1   0   0
    g h i 0 = 0   0   1   0
    j k l 1 = 3.5 3.5 3.5 1

The `<?>` is an unknown value of 1 in this example.

vertex
------

.. code-block:: text

    vertex <attrib> <id> <~> <edge> <point>

Represents a vertex of an `edge`_ entity and references a `point`_ entity.
Multiple `vertex` entities can reference the same `point`_ entity.


.. _sat.pdf: https://duckduckgo.com/?q=acis%2Bsat.pdf

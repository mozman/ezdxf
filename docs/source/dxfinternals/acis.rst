
.. module:: ezdxf.acis

.. ACIS_internals

ACIS Management Tool
====================

.. versionadded:: 0.18

These are low-level ACIS data management tools for analyzing, parsing and
creating ACIS data structures.
These tools cannot replace the official ACIS SDK due to the complexity of
the data structures, and without access to the full documentation it is very
cumbersome to reverse-engineer entities and their properties and the analysis
of ACIS data is limited to use as embedded data in DXF and DWG files.

It is possible to extract geometries made up only by polygonal faces and
maybe in the future it is also possible to create such polygon face meshes.

.. warning::

    Do not import from the implementation sub-package :mod:`ezdxf._acis`, always
    import from the API module :mod:`ezdxf.acis`.

Functions
=========

.. autofunction:: parse_sat(s: Union[str, Sequence[str]]) -> AcisBuilder

Classes
=======

AcisBuilder
-----------

.. class:: AcisBuilder

    Low level data structure to manage ACIS data files.

    .. attribute:: header

        :class:`AcisHeader`

    .. attribute:: entities

        List of all entities as :class:`RawEntity` instances managed by this
        builder.

    .. attribute:: bodies

        List of :class:`RawEntity` instances, on entry for each body entity.
        The body entity is always the root entity for an ACIS geometry.

    .. automethod:: dump_sat

        Write the final SAT file:

        .. code-block:: Python

            lines = asic_builder.dump_sat()
            with open("name.sat", "wt") as fp:
                fp.write("\n".join(lines))

    .. automethod:: query(func=lambda e: True) -> Iterator[RawEntity]

RawEntity
----------

.. class:: RawEntity

    Low level representation of an ACIS entity (node).

    .. attribute:: name

        entity type

    .. attribute:: id

        Unique id as int or -1 for id not acquired. The ACIS data embedded
        in DXF files do not use ids, dso the id is DXF files always -1.

    .. attribute:: data

        Generic data container. References to other entities (pointers) are
        :class:`RawEntity` instances, the basic types `float` and `int` are
        still strings.

        Avoid accessing the :attr:`data` directly and use the
        :meth:`parse_values` method instead to acquire data from an
        entity.

    .. attribute:: attributes

        Reference to entity attributes or a ``NULL_PTR``.

    .. automethod:: find_all(entity_type: str) -> list[RawEntity]

    .. automethod:: find_first(entity_type: str) -> RawEntity

    .. automethod:: find_path(path: str) -> RawEntity

    .. automethod:: find_entities(names: str) -> list[RawEntity]

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
be ignored if you use the flexible parsing methods of :class:`RawEntity`.
Writing support for this old formats is not required because all CAD
applications should be able to process version 7.0, even if embedded in a very
old DXF R2000 format (tested with Autodesk TrueView, BricsCAD and Nemetschek
Allplan).

The first goal is to document the entities which are required to represent
a geometry as polygonal faces (polygon face mesh), which can be converted into
a :class:`~ezdxf.render.MeshBuilder` object.

The entity data is described as stored in the :class:`RawEntity` class.
The entity type is stored in :attr:`~RawEntity.name`. The entity attributes
are stored as reference to an :class:`RawEntity` instance in
:attr:`~RawEntity.attributes` or the ``NULL_PTR`` instance if no attributes exist.
The :attr:`~RawEntity.id` is an integer value, but I have not seen any usage
of the id in DXF files, so it can always be -1.
The data fields are stored in the :attr:`~RawEntity.data` attribute, the
meaning of the data fields is the content of this section.
Each entry describes the fields starting after the `id` field
which is the 3rd record entry, as example the `transform` entity:

    transform $-1 -1 1 0 0 0 1 0 0 0 1 388.5 388.5 388.5 1 no_rotate no_reflect no_shear

The 1st field is the entity type `transform`, the 2nd field is the attribute
pointer, "$-1" is the ``NULL_PTR`` and the 3rd field is an id of -1, the
documentation of `transform`  starts at the 4th field.

transform
---------

structure::

    transform <attrib> <id> <a> <b> <c> <d> <e> <f> <g> <h> <i> <j> <k> <l> ...
        ... <?> no_rotate no_reflect no_shear

Example:

    transform $-1 -1 1 0 0 0 1 0 0 0 1 388.5 388.5 388.5 1 no_rotate no_reflect no_shear

Represents a transformation matrix without the last column in terms of the
usage in :class:`ezdxf.math.Matrix44`::

    a b c 0 = 1     0     0     0
    d e f 0 = 0     1     0     0
    g h i 0 = 0     0     1     0
    j k l 1 = 388.5 388.5 388.5 1

The <?> value is a 1, no idea if this value is the 4th homogeneous coordinate
of the translation row or something else.

... there is much TODO

.. _sat.pdf: https://duckduckgo.com/?q=acis%2Bsat.pdf

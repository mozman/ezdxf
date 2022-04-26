
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

Functions
=========

.. autofunction:: parse_sat

Classes
=======

AcisBuilder
-----------

.. class:: AcisBuilder

    Low level data structure to manage ACIS data files.

    .. attribute:: header

        :class:`AcisHeader`

    .. attribute:: entities

        List of all entities as :class:`AcisEntity` instances managed by this
        builder. Every entity managed by this builder has to be stored in the
        list.

    .. attribute:: bodies

        List of :class:`AcisEntity` instances, on entry for each body entity.
        The body entity is the root entity for a solid geometry.

    .. automethod:: dump_sat

        Write the final SAT file:

        .. code-block:: Python

            lines = asic_builder.dump_sat()
            with open("name.sat", "wt") as fp:
                fp.write("\n".join(lines))

    .. automethod:: query(func=lambda e: True) -> Iterator[AcisEntity]

AcisEntity
----------

.. class:: AcisEntity

    Low level representation of an ACIS entity (node).

    .. attribute:: name

        entity type

    .. attribute:: id

        Unique id as int or -1 for id not acquired. The ACIS data embedded
        in DXF files do not use ids, dso the id is DXF files always -1.

    .. attribute:: data

        Generic data container. References to other entities (pointers) are
        :class:`AcisEntity` instances, the basic types float and int are
        still strings.

        Avoid accessing the :attr:`data` directly and use the
        :meth:`parse_data` method instead to acquire data from an
        entity.

    .. attribute:: attributes

        Reference to entity attributes or a :attr:`acis.NULL_PTR`.

    .. automethod:: find_all

    .. automethod:: find_first

    .. automethod:: find_path

    .. automethod:: find_entities

    .. automethod:: parse_values

AcisHeader
----------

.. class:: AcisHeader

    Represents an ACIS file header.

    .. attribute:: version

        ACIS version as int

    .. attribute:: n_records

        Count of entities or 0

    .. attribute:: n_entities

        Count of entities

    .. attribute:: flags

        Bit 0: if 1 the file contains history data. This module does not read,
        write or manage history data!

    .. attribute:: acis_version

        ACIS version string

    .. attribute:: creation_date

        The creation date stored in the file as :class:`datetime.datetime`
        instance.

    .. attribute:: units_in_mm

        Count of millimeters which represent one drawing unit.

    .. automethod:: dumps

    .. automethod:: set_version

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
be ignored if you use the flexible parsing methods of :class:`AcisEntity`.
Writing support for this old formats is not required because all CAD
applications should be able to process version 7.0, even if embedded in a very
old DXF R2000 format (tested with Autodesk TrueView, BricsCAD and Nemetschek
Allplan).

The first goal is to document the entities which are required to represent
a geometry as polygonal faces (polygon face mesh), which can be converted into
a :class:`~ezdxf.render.MeshBuilder` object.

The entity data is described as stored in the :class:`AcisEntity` class.
The entity type is stored in :attr:`~AcisEntity.name`. The entity attributes
are stored as reference to an :class:`AcisEntity` instance in
:attr:`~AcisEntity.attributes` or the ``NULL_PTR`` instance if no attributes exist.
The :attr:`~AcisEntity.id` is an integer value, but I have not seen any usage
of the id in DXF files, so it can always be -1.
The data fields are stored in the :attr:`~AcisEntity.data` attribute, the
meaning of the data fields is the content of this section.
Each entry describes the fields starting after the `id` field
which is the 3rd record entry, as example the `transform` entity:

    transform $-1 -1 1 0 0 0 1 0 0 0 1 388.5 388.5 388.5 1 no_rotate no_reflect no_shear

The 1st field is the entity type `transform`, the 2nd field is the attribute
pointer, "$-1" is the ``NULL_PTR`` and the 3rd field is an id of -1, the
documentation of `transform`  starts at the 4th field.

transform
---------

Example:

    transform $-1 -1 1 0 0 0 1 0 0 0 1 388.5 388.5 388.5 1 no_rotate no_reflect no_shear

Represents a transformation matrix without the last column in terms of the
usage in :class:`ezdxf.math.Matrix44`::

    ... a b c d e f g h i j k l m no_rotate no_reflect no_shear

    a b c 0 = 1     0     0     0
    d e f 0 = 0     1     0     0
    g h i 0 = 0     0     1     0
    j k l m = 388.5 388.5 388.5 1

The `m` value is a 1, no idea if this value is the 4th homogeneous coordinate
of the translation row or something else.

... there is much TODO

.. _sat.pdf: https://duckduckgo.com/?q=acis%2Bsat.pdf

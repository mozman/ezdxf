
.. module:: ezdxf.acis

.. ACIS_internals

ACIS Management Tool
====================

.. versionadded:: 0.18

These are low level ACIS data management tools to parse or create ACIS data.
These tools can not replace the official ACIS SDK because of the complexity of
the data structures and without access to the full documentation its not
possible to parse or create all supported entities.

The ACIS data embedded in the DXF/DWG file format seems not to utilize all
features of the ACIS data format and so its possible to extract some
simple constructs like geometry only build of polygonal faces.

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

    .. automethod:: parse_data

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

    .. attribute:: history flag

        1 if the file contains history data. This module does not read, write or
        manage history data!

    .. attribute:: acis_version

        ACIS version string

    .. attribute:: creation date

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


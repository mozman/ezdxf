
.. module:: ezdxf.acis

.. ACIS_internals

ACIS Management Tool
====================

.. versionadded:: 0.18

These are low-level :term:`ACIS` data management tools for parsing and
creating simple and known ACIS data structures.

The main goals of these ACIS support libraries are:

    1. load and parse simple and known ACIS data structures
    2. create and export simple and known ACIS data structures

It is NOT a goal to edit and export arbitrary existing ACIS structures.

    Don't even try it!


These tools cannot replace the official :term:`ACIS` SDK due to the complexity of
the data structures and the absence of an :term:`ACIS` kernel. Without access to
the full documentation it is very cumbersome to reverse-engineer entities and
their properties, therefore the analysis of the :term:`ACIS` data structures is
limited to the use as embedded data in DXF and DWG files.

The `ezdxf` library does not provide an :term:`ACIS` kernel and there are no
plans for implementing one because this is far beyond my capabilities, but it
is possible to extract geometries made up only by planar polygonal faces and
maybe in the future it is also possible to create such polygon face meshes.

Functions
~~~~~~~~~

.. autofunction:: load(s: Union[str, bytes, bytearray]) -> list[Body]

Exceptions
~~~~~~~~~~

.. class:: AcisException

    Base exception of the :mod:`acis` module.

.. class:: InvalidLinkStructure

.. class:: ParsingError

.. class:: ExportError

Entities
~~~~~~~~

A document (`sat.pdf`_) about the basic ACIS 7.0 file format is floating in the
internet.

This section contains the additional information about the entities,
I got from analyzing the SAT data extracted from DXF files exported
by BricsCAD.

This documentation ignores the differences to the ACIS format prior to version
7.0 and all this differences are handled internally.

Writing support for ACIS version < 7.0 is not required because all CAD
applications should be able to process version 7.0, even if embedded in a very
old DXF R2000 format (tested with Autodesk TrueView, BricsCAD and Nemetschek
Allplan).

The first goal is to document the entities which are required to represent
a geometry as polygonal faces (polygon face mesh), which can be converted into
a :class:`~ezdxf.render.MeshBuilder` object.

AcisEntity
----------

.. class:: AcisEntity

Transform
---------


.. class:: Transform

    Represents an affine transformation operation.

Body
----

.. class:: Body

    Represents a solid geometry, which can consist of multiple :class:`Lump`
    entities.

Lump
----


.. class:: Lump

    The lump represents a connected entity and there can be multiple lumps in a
    :class:`Body`. Multiple lumps are linked together by the :attr:`next_lump`
    attribute which points to the next lump entity the last lump has a ``NONE_REF``
    as next lump. The :attr:`body` attribute references to the parent :class:`Body`
    entity.

Wire
----

.. class:: Wire

Shell
-----

.. class:: Shell

Subshell
--------

.. class:: Subshell


Face
----

.. class:: Face

Surface
--------

.. class:: Surface

Plane
-----

.. class:: Plane

Loop
-----

.. class:: Loop

Coedge
------

.. class:: Coedge

    The coedges are a double linked list where :attr:`next_coedge` points to the
    next coedge and :attr:`prev_codege` to the previous coedge.
    The :attr:`partner` field points to the partner coedge of the adjacent face.

    In a closed surface each edge is part of two adjacent faces with opposite
    orientations. The :attr:`edge` attribute references the geometric :class:`Edge`
    of the face and the :attr:`loop` attribute references to the parent :class:`Loop`
    entity.

Edge
----

.. class:: Edge


Vertex
------

.. class:: Vertex

    Represents a vertex of an :class:`Edge` entity and references a :class`Point`
    entity. Multiple :class:`Vertex` entities can reference the same :class:`Point`
    entity.

Point
-----

.. class:: Point

    Represents a point in space where :attr:`location` attribute represents
    the cartesian coordinates.

    .. attribute:: location

        Cartesian coordinates as :class:`~ezdxf.math.Vec3` instance



.. _sat.pdf: https://duckduckgo.com/?q=acis%2Bsat.pdf

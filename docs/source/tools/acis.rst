
.. module:: ezdxf.acis

.. ACIS_Tools

ACIS Tools
==========

.. versionadded:: 0.18

The :mod:`ezdxf.acis` sub-package provides some :term:`ACIS` data management
tools. The main goals of this tools are:

    1. load and parse simple and known :term:`ACIS` data structures
    2. create and export simple and known :term:`ACIS` data structures

It is NOT a goal to load and edit arbitrary existing :term:`ACIS` structures.

    Don't even try it!

These tools cannot replace the official :term:`ACIS` SDK due to the complexity of
the data structures and the absence of an :term:`ACIS` kernel.  Without access to
the full documentation it is very cumbersome to reverse-engineer entities and
their properties, therefore the analysis of the :term:`ACIS` data structures is
limited to the use as embedded data in DXF and DWG files.

The `ezdxf` library does not provide an :term:`ACIS` kernel and there are no
plans for implementing one because this is far beyond my capabilities, but it
is possible to extract geometries made up only by flat polygonal faces (polyhedron)
from ACIS data.  Exporting polyhedrons as ACIS data and loading this DXF file by
Autodesk products or BricsCAD works for :term:`SAT` data for DXF R2000-R2010 and
for :term:`SAB` data for DXF R2013-R2018.

.. module:: ezdxf.acis.api

.. important::

    Always import from the public interface module :mod:`ezdxf.acis.api`,
    the internal package and module structure may change in the future and
    imports from other modules than :mod:`api` will break.


Functions
~~~~~~~~~

.. autofunction:: load_dxf

Example:

.. code-block:: Python

    import ezdxf
    from ezdxf.acis import api as acis

    doc = ezdxf.readfile("your.dxf")
    msp = doc.modelspace()

    for e in msp.query("3DSOLID"):
        bodies = acis.load_dxf(e)
        ...

.. autofunction:: export_dxf

Example:

.. code-block:: Python

    import ezdxf
    from ezdxf.render import forms
    from ezdxf.acis import api as acis

    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    # create an ACIS body from a simple cube-mesh
    body = acis.body_from_mesh(forms.cube())
    solid3d = msp.add_3dsolid()
    acis.export_dxf(solid3d, [body])
    doc.saveas("cube.dxf")


.. autofunction:: load

.. autofunction:: export_sat

.. autofunction:: export_sab

.. autofunction:: mesh_from_body

The following images show the limitations of the :func:`mesh_from_body`
function. The first image shows the source ``3DSOLID`` entities with
subtraction of entities with flat and curved faces:

.. image:: gfx/solids-acis.png

Example script to extracts all flat polygonal faces as meshes:

.. code-block:: Python

    import ezdxf
    from ezdxf.acis import api as acis


    doc = ezdxf.readfile("3dsolids.dxf")
    msp = doc.modelspace()

    doc_out = ezdxf.new()
    msp_out = doc_out.modelspace()

    for e in msp.query("3DSOLID"):
        for body in acis.load_dxf(data):
            for mesh in acis.mesh_from_body(body):
                mesh.render_mesh(msp_out)
    doc_out.saveas("meshes.dxf")

The second image shows the flat faces extracted from the ``3DSOLID`` entities
and exported as :class:`~ezdxf.entities.Mesh` entities:

.. image:: gfx/solids-mesh.png

As you can see all faces which do not have straight lines as boundaries are
lost.

.. autofunction:: body_from_mesh

Exceptions
~~~~~~~~~~

.. class:: AcisException

    Base exception of the :mod:`ezdxf.acis` package.

.. class:: ParsingError

    Exception raised when loading invalid or unknown :term:`ACIS` structures.

.. class:: ExportError

    Exception raised when exporting invalid or unknown :term:`ACIS` structures.

.. class:: InvalidLinkStructure

    Exception raised when the internal link structure is damaged.

.. module:: ezdxf.acis.entities

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
a geometry as flat polygonal faces (polyhedron), which can be converted into
a :class:`~ezdxf.render.MeshBuilder` object.

Topology Entities:

    - :class:`Body`
    - :class:`Lump`
    - :class:`Shell`
    - :class:`Face`
    - :class:`Loop`
    - :class:`Coedge`
    - :class:`Edge`
    - :class:`Vertex`

Geometry Entities:

    - :class:`Transform`
    - :class:`Surface`
    - :class:`Plane`
    - :class:`Curve`
    - :class:`StraightCurve`
    - :class:`Point`

.. attribute:: NONE_REF

    Special sentinel entity which supports the :attr:`type` attribute and the
    :attr:`is_none` property. Represents all unset entities.
    Use this idiom on any entity type to check if an entity is unset::

        if entity.is_none:
            ...


AcisEntity
----------

.. class:: AcisEntity

    Base class for all ACIS entities.

    .. attribute:: type

        Name of the type as str.

    .. attribute:: id

        Unique id as int or -1 if not set.

    .. attribute:: attributes

        Reference to the first :class:`Attribute` entity (not supported).

    .. attribute:: is_none

        ``True`` for unset entities represented by the :attr:`NONE_REF`
        instance.

Transform
---------

.. class:: Transform(AcisEntity)

    Represents an affine transformation operation which transform the
    :class:`body` to the final location, size and rotation.

    .. attribute:: matrix

        Transformation matrix of type :class:`ezdxf.math.Matrix44`.

Body
----

.. class:: Body(AcisEntity)

    Represents a solid geometry, which can consist of multiple :class:`Lump`
    entities.

    .. attribute:: pattern

        Reference to the :class:`Pattern` entity.

    .. attribute:: lump

        Reference to the first :class:`Lump` entity

    .. attribute:: wire

        Reference to the first :class:`Wire` entity

    .. attribute:: transform

        Reference to the :class:`Transform` entity (optional)

    .. automethod:: lumps

    .. automethod:: append_lump

Pattern
-------

.. class:: Pattern(AcisEntity)

    Not implemented.

Lump
----


.. class:: Lump(AcisEntity)

    The lump represents a connected entity and there can be multiple lumps in a
    :class:`Body`. Multiple lumps are linked together by the :attr:`next_lump`
    attribute which points to the next lump entity the last lump has a ``NONE_REF``
    as next lump. The :attr:`body` attribute references to the parent :class:`Body`
    entity.

    .. attribute:: next_lump

        Reference to the next :class:`Lump` entity, the last lump references
        :attr:`NONE_REF`.

    .. attribute:: shell

        Reference to the :class:`Shell` entity.

    .. attribute:: body

        Reference to the parent :class:`Body` entity.

    .. automethod:: shells

    .. automethod:: append_shell

Wire
----

.. class:: Wire(AcisEntity)

    Not implemented.

Shell
-----

.. class:: Shell(AcisEntity)

    A shell defines the boundary of a solid object or a void (subtraction object).
    A shell references a list of :class:`Face` and :class:`Wire` entities.
    All linked :class:`Shell` entities are disconnected.

    .. attribute:: next_shell

        Reference to the next :class:`Shell` entity, the last shell references
        :attr:`NONE_REF`.

    .. attribute:: subshell

        Reference to the first :class:`Subshell` entity.

    .. attribute:: face

        Reference to the first :class:`Face` entity.

    .. attribute:: wire

        Reference to the first :class:`Wire` entity.

    .. attribute:: lump

        Reference to the parent :class:`Lump` entity.

    .. automethod:: faces

    .. automethod:: append_face

Subshell
--------

.. class:: Subshell(AcisEntity)

    Not implemented.

Face
----

.. class:: Face(AcisEntity)

    A face is the building block for :class:`Shell` entities.
    The boundary of a face is represented by one or more :class:`Loop` entities.
    The spatial geometry of the face is defined by the :attr:`surface` object,
    which is a bounded or unbounded parametric 3d surface (plane, ellipsoid,
    spline-surface, ...).

    .. attribute:: next_face

        Reference to the next :class:`Face` entity, the last face references
        :attr:`NONE_REF`.

    .. attribute:: loop

        Reference to the first :class:`Loop` entity.

    .. attribute:: shell

        Reference to the parent :class:`Shell` entity.

    .. attribute:: subshell

        Reference to the parent :class:`Subshell` entity.

    .. attribute:: surface

        Reference to the parametric :class:`Surface` geometry.

    .. attribute:: sense

        Boolean value of direction of the face normal with respect to the
        :class:`Surface` entity:

            - ``True``: "reversed" direction of the face normal
            - ``False``: "forward" for same direction of the face normal

    .. attribute:: double_sided

        Boolean value which indicates the sides of the face:

            - ``True``: the face is part of a hollow object and has two sides.
            - ``False``: the face is part of a solid object and has only one
              side which points away from the "material".

    .. attribute:: containment

        Unknown meaning.

        If :attr:`double_sided` is ``True``:

            - ``True`` is "in"
            - ``False`` is "out"

    .. automethod:: loops

    .. automethod:: append_loop

Loop
-----

.. class:: Loop(AcisEntity)

    A loop represents connected coedges which are building the boundaries of
    a :class:`Face`, there can be multiple loops for a single face e.g. faces
    can contain holes.
    The :attr:`coedge` attribute references the first :class:`Coedge` of the
    loop, the additional coedges are linked to this first :class:`Coedge`.
    In closed loops the coedges are organized as a circular list, in open loops
    the last coedge references the :attr:`NONE_REF` entity as :attr:`next_coedge`
    and the first coedge references the :attr:`NONE_REF` as :attr:`prev_coedge`.

    .. attribute:: next_loop

        Reference to the next :class:`Loop` entity, the last loop references
        :attr:`NONE_REF`.

    .. attribute:: coedge

        Reference to the first :class:`Coedge` entity.

    .. attribute:: face

        Reference to the parent :class:`Face` entity.

    .. automethod:: coedges

    .. automethod:: set_coedges

Coedge
------

.. class:: Coedge(AcisEntity)

    The coedges are a double linked list where :attr:`next_coedge` points to the
    next :class:`Coedge` and :attr:`prev_coedge` to the previous :class:`Coedge`.

    The :attr:`partner_coedge` attribute references the first partner
    :class:`Coedge` of an adjacent :class:`Face`, the partner edges are
    organized as a circular list. In a manifold closed surface each
    :class:`Face` is connected to one partner face by an :class:`Coedge`.
    In a non-manifold surface a face can have more than one partner face.


    .. attribute:: next_coedge

        References the next :class:`Coedge`, reference the :attr:`NONE_REF` if
        it is the last coedge in an open :class:`Loop`.

    .. attribute:: prev_coedge

        References the previous :class:`Coedge`, reference the :attr:`NONE_REF`
        if it is the first coedge in an open :class:`Loop`.

    .. attribute:: partner_coedge

        References the partner :class:`Coedge` of an adjacent :class:`Face`
        entity. The partner coedges are organized in a circular list.


    .. attribute:: edge

        References the :class:`Edge` entity.

    .. attribute:: loop

        References the parent :class:`Loop` entity.

    .. attribute:: pcurve

        References the :class:`PCurve` entity.

Edge
----

.. class:: Edge(AcisEntity)

    The :class:`Edge` entity represents the physical edge of an object. Its
    geometry is defined by the bounded portion of a parametric space curve.
    This bounds are stored as object-space :class:`Vertex` entities.

    .. attribute:: start_vertex

        The start :class:`Vertex` of the space-curve in object coordinates, if
        :attr:`NONE_REF` the curve is unbounded in this direction.

    .. attribute:: start_param

        The parametric starting bound for the parametric curve. Evaluating the
        :attr:`curve` for this parameter should return the coordinates of the
        :attr:`start_vertex`.


    .. attribute:: end_vertex

        The end :class:`Vertex` of the space-curve in object coordinates, if
        :attr:`NONE_REF` the curve is unbounded in this direction.

    .. attribute:: end_param

        The parametric end bound for the parametric curve.

    .. attribute:: coedge

        Parent :class:`Coedge` of this edge.

    .. attribute:: curve

        The parametric space-curve which defines this edge. The curve can be the
        :attr:`NULL_REF` while both :class:`Vertex` entities are the same vertex.
        In this case the :class:`Edge` represents an single point like the
        apex of a cone.

    .. attribute:: sense

        Boolean value which indicates the direction of the edge:

            - ``True``: the edge has the "reversed" direction as the underlying curve
            - ``False``: the edge has the same direction as the underlying curve ("forward")

    .. attribute:: convexity

        Unknown meaning, always the string "unknown".

Vertex
------

.. class:: Vertex(AcisEntity)

    Represents a vertex of an :class:`Edge` entity and references a
    :class:`Point` entity.

    .. attribute:: point

        The spatial location in object-space as :class:`Point` entity.

    .. attribute:: edge

        Parent :class:`Edge` of this vertex. The vertex can be referenced by
        multiple edges, anyone of them can be the parent of the vertex.

Surface
--------

.. class:: Surface(AcisEntity)

    Abstract base class for all parametric surfaces.

    The parameterization of any :class:`Surface` maps a 2D rectangle
    (u, v parameters) into the spatial object-space (x, y, z).

    .. attribute:: u_bounds

        Tuple of (start bound, end bound) parameters as two floats which define
        the bounds of the parametric surface in the u-direction, one or both
        values can be :attr:`math.inf` which indicates an unbounded state of
        the surface in that direction.

    .. attribute:: v_bounds

        Tuple of (start bound, end bound) parameters as two floats which define
        the bounds of the parametric surface in the v-direction, one or both
        values can be :attr:`math.inf` which indicates an unbounded state of
        the surface in that direction.

    .. automethod:: evaluate

Plane
-----

.. class:: Plane(Surface)

    Defines a flat plan as parametric surface.

    .. attribute:: origin

        Location vector of the origin of the flat plane as
        :class:`~ezdxf.math.Vec3`.

    .. attribute:: normal

        Normal vector of the plane as :class:`~ezdxf.math.Vec3`.
        Has to be an unit-vector!

    .. attribute:: u_dir

        Direction vector of the plane in u-direction as :class:`~ezdxf.math.Vec3`.
        Has to be an unit-vector!

    .. attribute:: v_dir

        Direction vector of the plane in v-direction as :class:`~ezdxf.math.Vec3`.
        Has to be an unit-vector!

    .. attribute:: reverse_v

       Boolean value which indicates the orientation of the coordinate system:

            - ``True``: left-handed system, the v-direction is reversed and the
              normal vector is :attr:`v_dir` cross :attr:`u_dir`.
            - ``False``: right-handed system and the normal vector is
              :attr:`u_dir` cross :attr:`v_dir`.

Curve
-----

.. class:: Curve(AcisEntity)

    Abstract base class for all parametric curves.

    The parameterization of any :class:`Curve` maps a 1D line (the parameter)
    into the spatial object-space (x, y, z).

    .. attribute:: bounds

        Tuple of (start bound, end bound) parameters as two floats which define
        the bounds of the parametric curve, one or both values can be
        :attr:`math.inf` which indicates an unbounded state of the curve in that
        direction.

    .. automethod:: evaluate


StraightCurve
-------------

.. class:: StraightCurve(Curve)

    Defines a straight line as parametric curve.

    .. attribute:: origin

        Location vector of the origin of the straight line as
        :class:`~ezdxf.math.Vec3`.

    .. attribute:: direction

        Direction vector the straight line as :class:`~ezdxf.math.Vec3`.
        Has to be an unit-vector!

PCurve
------

.. class:: PCurve(AcisEntity)

    Not implemented.

Point
-----

.. class:: Point(AcisEntity)

    Represents a point in the 3D object-space.

    .. attribute:: location

        Cartesian coordinates as :class:`~ezdxf.math.Vec3`.


.. _sat.pdf: https://duckduckgo.com/?q=acis%2Bsat.pdf

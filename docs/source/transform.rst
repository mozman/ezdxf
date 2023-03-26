.. _transform:

.. module:: ezdxf.transform

Transform
=========

.. versionadded:: 1.1

This module provides functions to apply transformations to multiple DXF
entities inplace in a more convenient and safe way:

.. code-block:: Python

    import math

    import ezdxf
    from ezdxf import transform

    doc = ezdxf.readfile("my.dxf")
    msp = doc.modelspace()

    log = transform.matrix(msp, m=transform.Matrix44.rotate_z(math.pi/2))

    # or more simple
    log = transform.z_rotate(msp, math.pi/2)

All functions handle errors by collecting them in an logging object without raising
an error.
The input `entities` are an iterable of :class:`~ezdxf.entities.DXFEntity`, which can be
any layout, :class:`~ezdxf.query.EntityQuery` or just a list/sequence of entities and
virtual entities are supported as well.

.. autosummary::
    :nosignatures:

    matrix
    matrix_ext
    translate
    scale_uniform
    scale
    x_rotate
    y_rotate
    z_rotate
    axis_rotate

.. autofunction:: matrix

.. autofunction:: matrix_ext

.. autofunction:: translate

.. autofunction:: scale_uniform

.. autofunction:: scale

.. autofunction:: x_rotate

.. autofunction:: y_rotate

.. autofunction:: z_rotate

.. autofunction:: axis_rotate

.. attribute:: MIN_SCALING_FACTOR

    Minimal scaling factor: 1e-12

.. class:: Error

    .. attribute:: TRANSFORMATION_NOT_SUPPORTED

        Entities without transformation support.

    .. attribute:: NON_UNIFORM_SCALING_ERROR

        Circular arcs (CIRCLE, ARC, bulges in POLYLINE and LWPOLYLINE entities)
        cannot be scaled non-uniformly.

    .. attribute:: INSERT_TRANSFORMATION_ERROR

        INSERT entities cannot represent a non-orthogonal target coordinate system.
        Maybe exploding the INSERT entities (recursively) beforehand can solve this
        issue, see function :func:`ezdxf.disassemble.recursive_decompose`.

    .. attribute:: VIRTUAL_ENTITY_NOT_SUPPORTED

        Transformation not supported for virtual entities e.g. non-uniform scaling for
        CIRCLE, ARC or POLYLINE with bulges

.. autoclass:: Logger

    A :class:`Sequence` of errors as :class:`Logger.Entry` instances.

    .. class:: Entry

        Named tuple representing a logger entry.

        .. attribute:: error

            :class:`Error` enum

        .. attribute:: msg

            error message as string

        .. attribute:: entity

            DXF entity which causes the error

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: __iter__

    .. automethod:: messages

.. module:: ezdxf.render.trace

Trace
=====

This module provides tools to create banded lines like LWPOLYLINE with width information.
Path rendering as quadrilaterals: :class:`~ezdxf.entities.Trace`,
:class:`~ezdxf.entities.Solid` or :class:`~ezdxf.entities.Face3d`.


.. autoclass:: TraceBuilder

    .. attribute:: abs_tol

        Absolute tolerance for floating point comparisons

    .. automethod:: append

    .. automethod:: close

    .. automethod:: faces

    .. automethod:: faces_wcs

    .. automethod:: virtual_entities

    .. automethod:: from_polyline

    .. method:: __len__

    .. method:: __getitem__

.. autoclass:: LinearTrace

    .. attribute:: abs_tol

        Absolute tolerance for floating point comparisons

    .. autoattribute:: is_started

    .. automethod:: add_station

    .. automethod:: faces

    .. automethod:: virtual_entities

.. autoclass:: CurvedTrace

    .. automethod:: faces

    .. automethod:: virtual_entities

    .. automethod:: from_arc

    .. automethod:: from_spline

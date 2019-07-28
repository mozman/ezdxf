Sun
===

.. module:: ezdxf.entities
    :noindex:

`SUN`_ entity defines properties of the sun.

======================== ===========================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'SUN'``
Factory function         creating a new SUN entity is not supported
======================== ===========================================================


.. _SUN: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-BB191D89-9302-45E4-9904-108AB418FAE1


.. class:: Sun

    .. attribute:: dxf.version

        Current version is ``1``.

    .. attribute:: dxf.status

        on = ``1`` or off = ``0``

    .. attribute:: dxf.color

        :ref:`ACI` value of the sun.

    .. attribute:: dxf.true_color

        :term:`True color` value of the sun.

    .. attribute:: dxf.intensity

        Intensity value in the range of ``0`` to ``1``. (float)

    .. attribute:: dxf.julian_day

        use :func:`~ezdxf.tools.calendardate` to convert :attr:`dxf.julian_day` to :class:`datetime.datetime` object.

    .. attribute:: dxf.time

        Day time in seconds past midnight. (int)

    .. attribute:: dxf.daylight_savings_time

    .. attribute:: dxf.shadows

        === =======================
        0   Sun do not cast shadows
        1   Sun do cast shadows
        === =======================

    .. attribute:: dxf.shadow_type

    .. attribute:: dxf.shadow_map_size

    .. attribute:: dxf.shadow_softness

Helix
=====

.. module:: ezdxf.entities
    :noindex:


The HELIX entity (`DXF Reference`_).

The helix curve is represented by a cubic B-spline curve, therefore the HELIX
entity is also derived from the SPLINE entity.

.. seealso::

    - `Wikipedia`_ article about the helix shape

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Spline`
DXF type                 ``'HELIX'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_helix`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-76DB3ABF-3C8C-47D1-8AFB-72942D9AE1FF

.. class:: Helix

    All points in :ref:`WCS` as (x, y, z) tuples

    .. attribute:: dxf.axis_base_point

        The base point of the helix axis (Vec3).

    .. attribute:: dxf.start_point

        The starting point of the helix curve (Vec3).
        This also defines the base radius as the distance from the start point
        to the axis base point.

    .. attribute:: dxf.axis_vector

        Defines the direction of the helix axis (Vec3).

    .. attribute:: dxf.radius

        Defines the top radius of the helix (float).

    .. attribute:: dxf.turn_height

        Defines the pitch (height if one helix turn) of the helix  (float).

    .. attribute:: dxf.turns

        The count of helix turns (float).

    .. attribute:: dxf.handedness

        Helix orientation (int).

        === ================================
        0   clock wise (left handed)
        1   counter clockwise (right handed)
        === ================================

    .. attribute:: dxf.constrain

        === =========================
        0   constrain turn height (pitch)
        1   constrain count of turns
        2   constrain total height
        === =========================

.. _Wikipedia: https://en.wikipedia.org/wiki/Helix

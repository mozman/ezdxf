UCS
====

.. module:: ezdxf.entities
    :noindex:

Defines an named or unnamed user coordinate system (`DXF Reference`_) for usage in CAD applications. This UCS table
entry does not interact with `ezdxf` in any way, to do coordinate transformations by `ezdxf` use the
:class:`ezdxf.math.UCS` class.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'UCS'``
Factory function         :meth:`Drawing.ucs.new`
======================== ==========================================

.. seealso::

    :ref:`ucs` and :ref:`ocs`

.. class:: UCSTableEntry

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.Table`).

    .. attribute:: dxf.name

        UCS name (str).

    .. attribute:: dxf.flags

        Standard flags (bit-coded values):

        === ========================================================
        16  If set, table entry is externally dependent on an xref
        32  If both this bit and bit 16 are set, the externally dependent xref
            has been successfully resolved
        64  If set, the table entry was referenced by at least one entity in the
            drawing the last time the drawing was edited. (This flag is only for
            the benefit of AutoCAD)
        === ========================================================

    .. attribute:: dxf.origin

        Origin  as (x, y, z) tuple

    .. attribute:: dxf.xaxis

        X-axis direction as (x, y, z) tuple

    .. attribute:: dxf.yaxis

        Y-axis direction as (x, y, z) tuple

    .. automethod:: ucs() -> UCS

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-1906E8A7-3393-4BF9-BD27-F9AE4352FB8B

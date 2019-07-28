AppID
=====

.. module:: ezdxf.entities
    :noindex:

Defines an APPID (`DXF Reference`_). These table entries maintain a set of names for all registered applications.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'APPID'``
Factory function         :meth:`Drawing.appids.new`
======================== ==========================================

.. class:: AppID

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.Table`).

    .. attribute:: dxf.name

        User-supplied (or application-supplied) application name (for extended data).

    .. attribute:: dxf.flags

        Standard flag values (bit-coded values):

        === =========================================================
        16  If set, table entry is externally dependent on an xref
        32  If both this bit and bit 16 are set, the externally dependent xref has been successfully resolved
        64  If set, the table entry was referenced by at least one entity in the drawing the last time the drawing was
            edited. (This flag is only for the benefit of AutoCAD)
        === =========================================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-6E3140E9-E560-4C77-904E-480382F0553E
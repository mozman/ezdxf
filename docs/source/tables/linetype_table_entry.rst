Linetype
========

.. module:: ezdxf.entities

Defines a linetype (`DXF Reference`_).

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'LTYPE'``
Factory function         :meth:`Drawing.linetypes.new`
======================== ==========================================

.. seealso::

    :ref:`tut_linetypes`

    DXF Internals: :ref:`ltype_table_internals`

.. class:: Linetype

    .. attribute:: dxf.name

        Linetype name (str).

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.Table`).

    .. attribute:: dxf.description

        Linetype description (str).

    .. attribute:: dxf.length

        Total pattern length in drawing units (float).

    .. attribute:: dxf.items

        Number of linetype elements (int).

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-F57A316C-94A2-416C-8280-191E34B182AC
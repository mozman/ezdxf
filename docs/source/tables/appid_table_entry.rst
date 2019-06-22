AppID
=====

.. module:: ezdxf.entities

.. class:: AppID

    Subclass of :class:`DXFEntity`

    Defines an AppID. These table entries maintain a set of names for all registered applications.

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
            edited. (This flag is for the benefit of AutoCAD commands. It can be ignored by most programs that read DXF
            files and need not be set by programs that write DXF files)
        === =========================================================
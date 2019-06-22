Linetype
========

.. module:: ezdxf.entities

.. seealso::

    :ref:`tut_linetypes`

    DXF Internals: :ref:`ltype_table_internals`

.. class:: Linetype

    Subclass of :class:`DXFEntity`

    Defines a linetype.

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

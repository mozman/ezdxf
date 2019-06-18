Line
====

.. module:: ezdxf.entities.line

.. class:: Line

    The LINE entity is a subclass :class:`~ezdxf.entities.dxfgfx.DXFGraphic` and represents a 3D line from :attr:`start`
    to :attr:`end`, :meth:`dxftype` returns ``'LINE'``. Create new lines in layouts and blocks by factory function
    :meth:`~ezdxf.graphicsfactory.CreatorInterface.add_line`.

    - :ref:`Common DXF attributes for DXF R12`
    - :ref:`Common DXF attributes for DXF R13 or later`

    .. attribute:: Line.dxf.start

        start point of line (2D/3D Point in :ref:`WCS`)

    .. attribute:: Line.dxf.end

        end point of line (2D/3D Point in :ref:`WCS`)

    .. attribute:: Line.dxf.thickness

        Line thickness in 3D space in direction :attr:`extrusion`, default value is ``0``. This value should not be
        confused with the :attr:`~ezdxf.entities.dxfgfx.DXFGraphic.dxf.lineweight` value.

    .. attribute:: Line.dxf.extrusion

        extrusion vector, default value is ``(0, 0, 1)``



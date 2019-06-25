BlockRecord
===========

.. module:: ezdxf.entities

BLOCK_RECORD (`DXF Reference`_) is a basic management structure for :class:`~ezdxf.layouts.BlockLayout` and
:class:`~ezdxf.layouts.Layout`. `ezdxf` take care of correct BLOCK_RECORDS management, users don't have to worry about.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'BLOCK_RECORD'``
Factory function         :meth:`Drawing.block_records.new`
======================== ==========================================



.. class:: BlockRecord

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.Table`).

    .. attribute:: dxf.name

        Name of associated BLOCK.

    .. attribute:: dxf.layout

        Handle to associated :class:`~ezdxf.entities.layout.DXFLayout`, if paperspace layout or modelspace else ``0``

    .. attribute:: dxf.explode

        ``1`` for BLOCK references can be exploded else ``0``

    .. attribute:: dxf.scale

        ``1`` for BLOCK references can be scaled else ``0``

    .. attribute:: dxf.units

        BLOCK insert units

        === ===================
        0   Unitless
        1   Inches
        2   Feet
        3   Miles
        4   Millimeters
        5   Centimeters
        6   Meters
        7   Kilometers
        8   Microinches
        9   Mils
        10  Yards
        11  Angstroms
        12  Nanometers
        13  Microns
        14  Decimeters
        15  Decameters
        16  Hectometers
        17  Gigameters
        18  Astronomical units
        19  Light years
        20  Parsecs
        21  US Survey Feet
        22  US Survey Inch
        23  US Survey Yard
        24  US Survey Mile
        === ===================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A1FD1934-7EF5-4D35-A4B0-F8AE54A9A20A
Arrows
======

.. module:: ezdxf.render.arrows

This module provides support for the AutoCAD standard arrow heads used in
DIMENSION, LEADER and MULTILEADER entities. Library user don't have to use the
:attr:`ARROWS` objects directly, but should know the arrow names stored in it as
attributes.

.. attribute:: ARROWS

    Single instance of :class:`_Arrows` to work with.


.. class:: _Arrows

    Management object for standard arrows.

    .. attribute:: __acad__

        Set of AutoCAD standard arrow names.

    .. attribute:: __ezdxf__

        Set of arrow names special to `ezdxf`.

    .. attribute:: closed_filled

    .. attribute:: dot

    .. attribute:: dot_small

    .. attribute:: dot_blank

    .. attribute:: origin_indicator

    .. attribute:: origin_indicator_2

    .. attribute:: open

    .. attribute:: right_angle

    .. attribute:: open_30

    .. attribute:: closed

    .. attribute:: dot_smallblank

    .. attribute:: none

    .. attribute:: oblique

    .. attribute:: box_filled

    .. attribute:: box

    .. attribute:: closed_blank

    .. attribute:: datum_triangle_filled

    .. attribute:: datum_triangle

    .. attribute:: integral

    .. attribute:: architectural_tick

    .. attribute:: ez_arrow

    .. attribute:: ez_arrow_blank

    .. attribute:: ez_arrow_filled

    .. automethod:: is_acad_arrow

    .. automethod:: is_ezdxf_arrow

    .. automethod:: insert_arrow(layout, name: str, insert: Vertex, size: float=1.0, rotation: float=0.0, *, dxfattribs=None) -> Vec2

    .. automethod:: render_arrow(layout, name: str, insert: Vertex, size: float=1.0, rotation: float=0.0, *, dxfattribs=None) -> Vec2

    .. automethod:: virtual_entities(name: str, insert: Vertex, size: float=0.625, rotation: float=0.0, *, dxfattribs=None) -> Iterator[DXFGraphic]

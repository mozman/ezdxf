Arrows
======

.. module:: ezdxf.render.arrows

This module provides support for the AutoCAD standard arrow heads used in
DIMENSION, LEADER and MULTILEADER entities. Library user don't have to use the
:attr:`ARROWS` objects directly, but should know the arrow names stored in it as
attributes. The arrow names should be accessed that way:

.. code-block:: python

    import ezdxf

    arrow = ezdxf.ARROWS.closed_filled


.. attribute:: ARROWS

    Single instance of :class:`_Arrows` to work with.


.. class:: _Arrows

    Management object for standard arrows.

    .. attribute:: __acad__

        Set of AutoCAD standard arrow names.

    .. attribute:: __ezdxf__

        Set of arrow names special to `ezdxf`.

    .. attribute:: architectural_tick

        .. image:: gfx/_ARCHTICK.png

    .. attribute:: closed_filled

        .. image:: gfx/_CLOSEDFILLED.png

    .. attribute:: dot

        .. image:: gfx/_DOT.png

    .. attribute:: dot_small

        .. image:: gfx/_DOTSMALL.png

    .. attribute:: dot_blank

        .. image:: gfx/_DOTBLANK.png

    .. attribute:: origin_indicator

        .. image:: gfx/_ORIGIN.png

    .. attribute:: origin_indicator_2

        .. image:: gfx/_ORIGIN2.png

    .. attribute:: open

        .. image:: gfx/_OPEN.png

    .. attribute:: right_angle

        .. image:: gfx/_OPEN90.png

    .. attribute:: open_30

        .. image:: gfx/_OPEN30.png

    .. attribute:: closed

        .. image:: gfx/_CLOSED.png

    .. attribute:: dot_smallblank

        .. image:: gfx/_SMALL.png

    .. attribute:: none

        .. image:: gfx/_NONE.png

    .. attribute:: oblique

        .. image:: gfx/_OBLIQUE.png

    .. attribute:: box_filled

        .. image:: gfx/_BOXFILLED.png

    .. attribute:: box

        .. image:: gfx/_BOXBLANK.png

    .. attribute:: closed_blank

        .. image:: gfx/_CLOSEDBLANK.png

    .. attribute:: datum_triangle_filled

        .. image:: gfx/_DATUMFILLED.png

    .. attribute:: datum_triangle

        .. image:: gfx/_DATUMBLANK.png

    .. attribute:: integral

        .. image:: gfx/_INTEGRAL.png

    .. attribute:: ez_arrow

        .. image:: gfx/EZ_ARROW.png

    .. attribute:: ez_arrow_blank

        .. image:: gfx/EZ_ARROW_BLANK.png

    .. attribute:: ez_arrow_filled

        .. image:: gfx/EZ_ARROW_FILLED.png

    .. automethod:: is_acad_arrow

    .. automethod:: is_ezdxf_arrow

    .. automethod:: insert_arrow

    .. automethod:: render_arrow

    .. automethod:: virtual_entities

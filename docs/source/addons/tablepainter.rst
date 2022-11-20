.. _table_painter:

.. module:: ezdxf.addons.tablepainter

TablePainter
============

This is an add-on for drawing tables build from DXF primitives.

This add-on was created for porting :mod:`dxfwrite` projects to :mod:`ezdxf` and
was not officially documented for :mod:`ezdxf` versions prior the 1.0 release.
For the 1.0 version of :mod:`ezdxf`, this class was added as an officially
documented add-on because full support for the ACAD_TABLE entity
is very unlikely due to the enormous complexity for both the entity itself,
as well as for the required infrastructure and also the lack of an usable
documentation to implement all that features.

.. important::

    This add-on is not related to the ACAD_TABLE entity at all and and does not
    create ACAD_TABLE entities!


The table cells can contain multi-line text or BLOCK references, and you can
create your own cell type by extending the :class:`CustomCell`
class.

A table cell can span over multiple columns and/or rows.

Text cells can contain text with an arbitrary rotation angle, or letters can be
stacked from top to bottom.

BlockCells contains block references (INSERT) created from a BLOCK
definition, if the block definition contains attribute definitions
(ATTDEF), these attributes will be added to the block reference as ATTRIB
entities.

.. note::

    The DXF format does not support clipping boxes, therefore the render method
    of any cell can render beyond their borders!

.. seealso::

    - Example script: `table_painter_addon.py`_

TablePainter
------------

.. autoclass:: TablePainter

    .. attribute:: bg_layer_name: str

        background layer name, layer for the background SOLID entities,
        default is "TABLEBACKGROUND"

    .. attribute:: fg_layer_name: str

        foreground layer name, layer for the cell content, default is
        "TABLECONTENT"

    .. attribute:: grid_layer_name: str

        table grid layer name, layer for the cell border lines, default is
        "TABLEGRID"

    .. automethod:: set_col_width

    .. automethod:: set_row_height

    .. automethod:: text_cell

    .. automethod:: block_cell

    .. automethod:: set_cell

    .. automethod:: get_cell

    .. automethod:: new_cell_style

    .. automethod:: get_cell_style

    .. automethod:: new_border_style

    .. automethod:: frame

    .. automethod:: render

Cell
----

.. class:: Cell

    Abstract base class for table cells.


TextCell
--------

.. class:: TextCell

    Implements a cell type containing a multi-line text. Uses the
    :class:`~ezdxf.addons.MTextSurrogate` add-on to render the multi-line
    text, therefore the content of these cells is compatible to DXF R12.

    .. important::

        Use the factory method :meth:`TablePainter.text_cell` to
        instantiate text cells.

BlockCell
---------

.. autoclass:: BlockCell

    Implements a cell type containing a block reference.

    .. important::

        Use the factory method :meth:`TablePainter.block_cell` to
        instantiate block cells.

CustomCell
----------

.. class:: CustomCell

    Base class to implement custom cells. Overwrite the :meth:`render` method
    to render the cell. The custom cell type has to be instantiated by the
    user and added to the table by the :meth:`TablePainter.set_cell` method.

    .. automethod:: render

        The render space is defined by the argument `coords` which is a tuple of
        4 float values in the order: left, right, top, bottom. These values are
        layout coordinates in drawing units.
        The DXF format does not support clipping boxes, therefore the render method
        can render beyond these borders!

CellStyle
---------

.. autoclass:: CellStyle

    .. attribute:: text_style: str

        :class:`~ezdxf.entities.Textstyle` name as string, ignored by :class:`BlockCell`

    .. attribute:: char_height: float

        text height in drawing units, ignored by :class:`BlockCell`

    .. attribute:: line_spacing: float

        line spacing in percent, distance of line base points = :attr:`char_height`
        * :attr:`line_spacing`, ignored by :class:`BlockCell`

    .. attribute:: scale_x: float

        text stretching factor (width factor) or block reference x-scaling factor

    .. attribute:: scale_y: float

        block reference y-scaling factor, ignored by :class:`TextCell`

    .. attribute:: textcolor: int

        :ref:`ACI` for text, ignored by :class:`BlockCell`

    .. attribute:: rotation: float

        text or block rotation in degrees

    .. attribute:: stacked: bool

        Stacks letters of :class:`TextCell` instances from top to bottom without
        rotating the characters if ``True``, ignored by :class:`BlockCell`

    .. attribute:: align: MTextEntityAlignment

        text and block alignment, see :class:`ezdxf.enums.MTextEntityAlignment`

    .. attribute:: margin_x: float

        left and right cell margin in drawing units

    .. attribute:: margin_y: float

        top and bottom cell margin in drawing units

    .. attribute:: bg_color: int

         cell background color as :ref:`ACI`, ignored by :class:`BlockCell`

    .. attribute:: left: BorderStyle

        left cell border style

    .. attribute:: top: BorderStyle

        top cell border style

    .. attribute:: right: BorderStyle

        right cell border style

    .. attribute:: bottom: BorderStyle

        bottom cell border style

    .. automethod:: set_border_status

    .. automethod:: set_border_style

    .. automethod:: get_default_border_style

BorderStyle
-----------

.. autoclass:: BorderStyle

    .. attribute:: status: bool

        border status, ``True``  for visible, ``False`` for hidden

    .. attribute:: color: int

        :ref:`ACI`

    .. attribute:: linetype: str

        linetype name as string, default is "BYLAYER"

    .. attribute:: priority: int

        drawing priority, higher values cover lower values

.. _table_painter_addon.py: https://github.com/mozman/ezdxf/blob/master/examples/addons/table_painter_addon.py
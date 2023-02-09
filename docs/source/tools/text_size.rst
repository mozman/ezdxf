.. _Text Size Tools:

Text Size Tools
===============

.. module:: ezdxf.tools.text_size


.. class:: ezdxf.tools.text_size.TextSize

    A frozen dataclass as return type for the :func:`text_size` function.

    .. attribute:: width

        The text width in drawing units (float).

    .. attribute:: cap_height

        The font cap-height in drawing units (float).

    .. attribute:: total_height

        The font total-height = cap-height + descender-height in drawing units (float).

.. autofunction:: text_size


.. class:: ezdxf.tools.text_size.MTextSize

    A frozen dataclass as return type for the :func:`mtext_size` function.

    .. attribute:: total_width

        The total width in drawing units (float)

    .. attribute:: total_height

        The total height in drawing units (float), same as ``max(column_heights)``.

    .. attribute:: column_width

        The width of a single column in drawing units (float)

    .. attribute:: gutter_width

        The space between columns in drawing units (float)

    .. attribute:: column_heights

        A tuple of columns heights (float) in drawing units. Contains at least
        one column height and the column height is 0 for an empty column.

    .. attribute:: column_count

        The count of columns (int).

.. autofunction:: mtext_size

.. autofunction:: estimate_mtext_extents

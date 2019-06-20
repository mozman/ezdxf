.. _layout_manager:

Layout Manager
==============

.. module:: ezdxf.layouts

The layout manager is unique to each DXF drawing, access the layout manager as :attr:`~ezdxf.drawing.Drawing.layouts`
attribute of the :class:`~ezdxf.drawing.Drawing` object.

.. class:: Layouts

    The :class:`Layouts` class manages paperspace layouts and the modelspace.

    .. automethod:: __len__

    .. automethod:: __contains__

    .. automethod:: __iter__() -> Iterable[Layout]

    .. automethod:: modelspace() -> Layout

    .. automethod:: names

    .. automethod:: get(name: str) -> Layout

    .. automethod:: get_layout_for_entity(entity: DXFEntity) -> Layout

    .. automethod:: rename

    .. automethod:: names_in_taborder

    .. automethod:: new(name: str, dxfattribs: dict = None) -> Layout

    .. automethod:: active_layout() -> Layout

    .. automethod:: set_active_layout

    .. automethod:: delete

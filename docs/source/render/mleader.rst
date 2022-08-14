.. module:: ezdxf.render
    :noindex:

MultiLeaderBuilder
==================

These are helper classes to build :class:`~ezdxf.entities.MultiLeader` entities
in an easy way.  The :class:`MultiLeader` entity supports two kinds of content,
for each exist a specialized builder class:

- :class:`MultiLeaderMTextBuilder` for :class:`~ezdxf.entities.MText` content
- :class:`MultiLeaderBlockBuilder` for :class:`~ezdxf.entities.Block` content

The usual steps of the building process are:

    1. create entity by a factory method

        - :meth:`~ezdxf.layouts.BaseLayout.add_multileader_mtext`
        - :meth:`~ezdxf.layouts.BaseLayout.add_multileader_block`

    2. set the content

        - :meth:`MultiLeaderMTextBuilder.set_content`
        - :meth:`MultiLeaderBlockBuilder.set_content`
        - :meth:`MultiLeaderBlockBuilder.set_attribute`

    3. set properties

        - :meth:`MultiLeaderBuilder.set_arrow_properties`
        - :meth:`MultiLeaderBuilder.set_connection_properties`
        - :meth:`MultiLeaderBuilder.set_connection_types`
        - :meth:`MultiLeaderBuilder.set_leader_properties`
        - :meth:`MultiLeaderBuilder.set_mleader_style`
        - :meth:`MultiLeaderBuilder.set_overall_scaling`

    4. add one or more leader lines

        - :meth:`MultiLeaderBuilder.add_leader_line`

    5. finalize building process

        - :meth:`MultiLeaderBuilder.build`

The :ref:`tut_mleader` shows how to use these helper classes in more detail.

.. versionadded:: 0.18

.. class:: MultiLeaderBuilder

    Abstract base class to build :class:`~ezdxf.entities.MultiLeader` entities.

    .. autoproperty:: context

    .. autoproperty:: multileader

    .. automethod:: add_leader_line

    .. automethod:: build

    .. automethod:: set_arrow_properties

    .. automethod:: set_connection_properties

    .. automethod:: set_connection_types

    .. automethod:: set_leader_properties

    .. automethod:: set_mleader_style

    .. automethod:: set_overall_scaling


MultiLeaderMTextBuilder
-----------------------

Specialization of :class:`MultiLeaderBuilder` to build :class:`~ezdxf.entities.MultiLeader`
with MTEXT content.

.. class:: MultiLeaderMTextBuilder

    .. automethod:: set_content

    .. automethod:: quick_leader

MultiLeaderBlockBuilder
-----------------------

Specialization of :class:`MultiLeaderBuilder` to build :class:`~ezdxf.entities.MultiLeader`
with BLOCK content.

.. class:: MultiLeaderBlockBuilder

    .. autoproperty:: block_layout

    .. autoproperty:: extents

    .. automethod:: set_content

    .. automethod:: set_attribute

Enums
-----

.. autoclass:: LeaderType

    .. attribute:: none

    .. attribute:: straight_lines

    .. attribute:: splines

.. autoclass:: ConnectionSide

    .. attribute:: left

    .. attribute:: right

    .. attribute:: top

    .. attribute:: bottom

.. autoclass:: HorizontalConnection

    .. attribute:: by_style

    .. attribute:: top_of_top_line

    .. attribute:: middle_of_top_line

    .. attribute:: middle_of_text

    .. attribute:: middle_of_bottom_line

    .. attribute:: bottom_of_bottom_line

    .. attribute:: bottom_of_bottom_line_underline

    .. attribute:: bottom_of_top_line_underline

    .. attribute:: bottom_of_top_line

    .. attribute:: bottom_of_top_line_underline_all

.. autoclass:: VerticalConnection

    .. attribute:: by_style

    .. attribute:: center

    .. attribute:: center_overline

.. autoclass:: TextAlignment

    .. attribute:: left

    .. attribute:: center

    .. attribute:: right

.. autoclass:: BlockAlignment

    .. attribute:: center_extents

    .. attribute:: insertion_point


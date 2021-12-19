.. module:: ezdxf.render
    :noindex:

MultiLeaderBuilder
==================

.. versionadded:: 0.18

.. class:: MultiLeaderBuilder

    Abstract base class to build :class:`~ezdxf.entities.MultiLeader` entities.

.. class:: MultiLeaderMTextBuilder

    Specialization of :class:`MultiLeaderBuilder` to build :class:`~ezdxf.entities.MultiLeader`
    with MTEXT content.

.. class:: MultiLeaderBlockBuilder

    Specialization of :class:`MultiLeaderBuilder` to build :class:`~ezdxf.entities.MultiLeader`
    with BLOCK content.

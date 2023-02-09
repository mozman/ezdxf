Entities Section
================

.. module:: ezdxf.sections.entities

The ENTITIES section is the home of all entities of the :class:`~ezdxf.layouts.Modelspace`
and the active :class:`~ezdxf.layouts.Paperspace` layout.  This is a real section in the
DXF file but in `ezdxf` the :class:`EntitySection` is just a linked entity space of
these two layouts.

.. seealso::

    DXF Internals: :ref:`entities_section_internals`

.. class:: EntitySection

    .. automethod:: __iter__

    .. automethod:: __len__


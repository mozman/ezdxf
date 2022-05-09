Entities Section
================

.. module:: ezdxf.sections.entities

The ENTITIES section is the home of all :class:`~ezdxf.layouts.Modelspace` and active
:class:`~ezdxf.layouts.Paperspace` layout entities. This is a real section in the DXF file,
for `ezdxf` the :class:`EntitySection` is just a proxy for modelspace and the active paperspace linked together.

.. seealso::

    DXF Internals: :ref:`entities_section_internals`

.. class:: EntitySection

    .. automethod:: __iter__

    .. automethod:: __len__


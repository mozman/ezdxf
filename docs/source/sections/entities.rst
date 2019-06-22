Entities Section
================

.. module:: ezdxf.sections.entities

The ENTITIES section is the home of all modelspace and active paperspace layout entities. This is a real section in the
DXF file, in `ezdxf` is the :class:`EntitySection` just a proxy for modelspace and the active paperspace linked together.

.. seealso::

    DXF Internals: :ref:`entities_section_internals`

.. class:: EntitySection

    .. automethod:: __iter__() -> Iterable[DXFEntity]

    .. automethod:: __len__() -> int


MultiLeader
===========

.. module:: ezdxf.entities
    :noindex:

.. versionadded:: 0.18

The MULTILEADER entity (`DXF Reference`_) represents one ore more leaders,
made up of one or more vertices (or spline fit points) and an arrowhead.
In contrast to the :class:`Leader` entity the text- or block content is part of
the MULTILEADER entity.

AutoCAD, BricsCAD and maybe other CAD applications do accept ``'MLEADER'`` as
type string but they always create entities with ``'MULTILEADER'`` as type
string.

Because of the complexity of the MLEADER entity it is recommend to use the
:class:`~ezdxf.render.MultiLeaderBuilder` to construct the entity.

The visual design is based on an associated :class:`~ezdxf.entities.MLeaderStyle`,
but almost all attributes are also stored in the MULTILEADER entity itself.

The attribute :attr:`MultiLeader.dxf.property_override_flags` should indicate
which MLEADERSTYLE attributes are overridden by MULTILEADER attributes,
but these flags do not always reflect the state of overridden attributes.
The `ezdxf` MULTILEADER renderer uses always the attributes from
the MULTILEADER entity and ignores the override flags.

.. seealso::

    - :class:`ezdxf.entities.MLeaderStyle`
    - :class:`ezdxf.render.MultiLeaderBuilder`
    - :ref:`tut_mleader`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'MULTILEADER'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_multileader`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72D20B8C-0F5E-4993-BEB7-0FCF94F32BE0


.. class:: MultiLeader

    .. automethod:: virtual_entities() -> Iterable[DXFGraphic]

    .. automethod:: explode(target_layout: BaseLayout = None) -> EntityQuery

    .. automethod:: transform(m: Matrix44) -> MultiLeader


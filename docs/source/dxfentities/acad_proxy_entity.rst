ACADProxyEntity
===============

.. module:: ezdxf.entities
    :noindex:


An ACAD_PROXY_ENTITY (`DXF Reference`_) is a proxy entity that represents an entity
created by an Autodesk or 3rd party application.
It stores the graphics and data of the original entity.

The internals of this entity are unknown, so the entity cannot be copied or transformed.
However, `ezdxf` can extract the proxy graphic from these entities as virtual entities
or replace (explode) the entire entity with its proxy graphic. The meaning and data of
this entity is lost when the entity is exploded.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'ACAD_PROXY_ENTITY'``
Factory function         not supported
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. class:: ACADProxyEntity

    .. automethod:: virtual_entities

    .. automethod:: explode

.. _DXF Reference: https://help.autodesk.com/view/OARX/2019/ENU/?guid=GUID-89A690F9-E859-4D57-89EA-750F3FB76C6B
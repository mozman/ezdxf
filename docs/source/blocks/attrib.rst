Attrib
======

.. module:: ezdxf.entities

The ATTRIB (`DXF Reference`_) entity represents a text value associated with a tag.
In most cases an ATTRIB is appended to an :class:`Insert` entity, but it can also
appear as standalone entity.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Text`
DXF type                 ``'ATTRIB'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_attrib` (stand alone entity)
Factory function         :meth:`Insert.add_attrib` (attached to :class:`Insert`)
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. seealso::

    :ref:`tut_blocks`

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Attrib

    ATTRIB supports all DXF attributes and methods of parent class :class:`Text`.

    .. attribute:: dxf.tag

        Tag to identify the attribute (str)

    .. attribute:: dxf.text

        Attribute content as text (str)

    .. attribute:: is_invisible

        Attribute is invisible (does not appear).

    .. attribute:: is_const

        This is a constant attribute.

    .. attribute:: is_verify

        Verification is required on input of this attribute. (CAD application feature)

    .. attribute:: is_preset

        No prompt during insertion. (CAD application feature)

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-7DD8B495-C3F8-48CD-A766-14F9D7D0DD9B
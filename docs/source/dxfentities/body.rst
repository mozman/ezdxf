Body
====

.. module:: ezdxf.entities
    :noindex:

BODY entity (`DXF Reference`_) created by an ACIS geometry kernel provided by
the `Spatial Corp.`_

.. seealso::

    `Ezdxf` has only very limited support for ACIS based entities, for more
    information see the FAQ: :ref:`faq003`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'BODY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_body`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided
    factory functions!

.. class:: Body

    .. attribute:: dxf.version

        Modeler format version number, default value is 1

    .. attribute:: dxf.flags

        Require DXF R2013.

    .. attribute:: dxf.uid

        Require DXF R2013.

    .. autoproperty:: acis_data

    .. autoproperty:: sat

    .. autoproperty:: sab

    .. autoproperty:: has_binary_data

    .. automethod:: tostring


.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-7FB91514-56FF-4487-850E-CF1047999E77
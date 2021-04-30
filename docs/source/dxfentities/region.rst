Region
======

.. module:: ezdxf.entities
    :noindex:

REGION (`DXF Reference`_) created by an ACIS based geometry kernel provided by
the `Spatial Corp.`_

.. seealso::

    `Ezdxf` will never create or interpret ACIS data, for more information see
    the FAQ: :ref:`faq003`


======================== ==========================================
Subclass of              :class:`ezdxf.entities.Body`
DXF type                 ``'REGION'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_region`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Region

    Same attributes and methods as parent class :class:`Body`.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-644BF0F0-FD79-4C5E-AD5A-0053FCC5A5A4
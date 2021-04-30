Body
====

.. module:: ezdxf.entities
    :noindex:

BODY (`DXF Reference`_) created by an ACIS based geometry kernel provided by
the `Spatial Corp.`_

.. seealso::

    `Ezdxf` will never create or interpret ACIS data, for more information see
    the FAQ: :ref:`faq003`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'BODY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_body`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Body

    .. attribute:: dxf.version

        Modeler format version number, default value is ``1``

    .. attribute:: dxf.flags

        Require DXF R2013.

    .. attribute:: dxf.uid

        Require DXF R2013.

    .. attribute:: acis_data

        Get/Set ACIS text data as list of strings for DXF R2000 to R2010 and binary encoded ACIS data for DXF R2013
        and later as list of bytes.

    .. autoattribute:: has_binary_data

    .. automethod:: tostring

    .. automethod:: tobytes

    .. automethod:: set_text

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-7FB91514-56FF-4487-850E-CF1047999E77
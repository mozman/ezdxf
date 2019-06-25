Solid3d
=======

.. module:: ezdxf.entities

3DSOLID (`DXF Reference`_) created by an ACIS based geometry kernel provided by the `Spatial Corp.`_

`ezdxf` will never interpret ACIS source code, don't ask me for this feature.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Body`
DXF type                 ``'3DSOLID'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_3dsolid`
Required DXF version     DXF R2000
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Solid3d

    Same attributes and methods as parent class :class:`Body`.

    .. attribute:: dxf.history_handle

        Handle to history object.


.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-19AB1C40-0BE0-4F32-BCAB-04B37044A0D3
Region
======

.. module:: ezdxf.entities

An object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_

`ezdxf` will never interpret ACIS source code, don't ask me for this feature.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Body`
DXF type                 ``'REGION'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_region`
Required DXF version     DXF R2000
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Region

    Same attributes and methods as parent class :class:`Body`.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

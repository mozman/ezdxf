Wipeout
=======

.. module:: ezdxf.entities
    :noindex:

THE WIPEOUT (`DXF Reference`_) entity is a polygonal area that masks underlying
objects with the current background color. The WIPEOUT entity is base on the
IMAGE entity, but usage does not require any knowledge about the IMAGE entity.


======================== ==========================================
Subclass of              :class:`ezdxf.entities.Image`
DXF type                 ``'WIPEOUT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_wipeout`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Wipeout

    .. automethod:: set_wipeout_area

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-2229F9C4-3C80-4C67-9EDA-45ED684808DC
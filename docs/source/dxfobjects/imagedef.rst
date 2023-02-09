ImageDef
========

.. module:: ezdxf.entities
    :noindex:

The `IMAGEDEF`_ entity defines an image file, which can be placed by the :class:`Image`
entity.

======================== ===========================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'IMAGEDEF'``
Factory function (1)     :meth:`ezdxf.document.Drawing.add_image_def`
Factory function (2)     :meth:`ezdxf.sections.objects.ObjectsSection.add_image_def`
======================== ===========================================================

.. warning::

    Do not instantiate object classes by yourself - always use the provided factory functions!

.. _IMAGEDEF: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-EFE5319F-A71A-4612-9431-42B6C7C3941F


.. class:: ImageDef

    .. attribute:: dxf.class_version

        Current version is 0.

    .. attribute:: dxf.filename

        Relative (to the DXF file) or absolute path to the image file as string.

    .. attribute:: dxf.image_size

        Image size in pixel as (x, y) tuple.

    .. attribute:: dxf.pixel_size

        Default size of one pixel in drawing units as (x, y) tuple.

    .. attribute:: dxf.loaded

        0 = unloaded; 1 = loaded, default is 1

    .. attribute:: dxf.resolution_units

        === ==================
        0   No units
        2   Centimeters
        5   Inch
        === ==================

        default is 0


ImageDefReactor
===============


.. class:: ImageDefReactor

    .. attribute:: dxf.class_version

    .. attribute:: dxf.image_handle
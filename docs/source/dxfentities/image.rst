Image
=====

.. module:: ezdxf.entities
    :noindex:

The IMAGE entity (`DXF Reference`_) represents a raster image, the image file itself is
not embedded into the DXF file, it is always a separated file.
The IMAGE entity is like a block reference, it can be used to add the image multiple times
at different locations with different scale and rotation angles.  Every IMAGE entity
requires an image definition, see entity :class:`ImageDef`.
`Ezdxf` creates only images in the xy-plan, it's possible to place images in 3D space,
therefore the :attr:`Image.dxf.u_pixel` and the :attr:`Image.dxf.v_pixel` vectors
has to be set accordingly.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'IMAGE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_image`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Image

    .. attribute:: dxf.insert

        Insertion point, lower left corner of the image (3D Point in :ref:`WCS`).

    .. attribute:: dxf.u_pixel

        U-vector of a single pixel as (x, y, z) tuple. This vector points along the
        visual bottom of the image, starting at the insertion point.

    .. attribute:: dxf.v_pixel

        V-vector of a single pixel as (x, y, z) tuple. This vector points along the
        visual left side of the image, starting at the insertion point.

    .. attribute:: dxf.image_size

        Image size in pixels as (x, y) tuple

    .. attribute:: dxf.image_def_handle

        Handle to the image definition entity, see :class:`ImageDef`

    .. attribute:: dxf.flags

        =================================== ======= ===========
        :attr:`Image.SHOW_IMAGE`            1       Show image
        :attr:`Image.SHOW_WHEN_NOT_ALIGNED` 2       Show image when not aligned with screen
        :attr:`Image.USE_CLIPPING_BOUNDARY` 4       Use clipping boundary
        :attr:`Image.USE_TRANSPARENCY`      8       Transparency is on
        =================================== ======= ===========

    .. attribute:: dxf.clipping

        Clipping state:

        === ============
        0   clipping off
        1   clipping on
        === ============

    .. attribute:: dxf.brightness

        Brightness value in the range [0, 100], default is 50

    .. attribute:: dxf.contrast

        Contrast value in the range [0, 100], default is 50

    .. attribute:: dxf.fade

        Fade value in the range [0, 100], default is 0

    .. attribute:: dxf.clipping_boundary_type

        === ============
        1   Rectangular
        2   Polygonal
        === ============

    .. attribute:: dxf.count_boundary_points

        Number of clip boundary vertices, this attribute is maintained by `ezdxf`.

    .. attribute:: Image.dxf.clip_mode

        === ========
        0   Outside
        1   Inside
        === ========

        requires DXF R2010 or newer

    .. autoattribute:: boundary_path

    .. autoattribute:: image_def

    .. automethod:: reset_boundary_path

    .. automethod:: set_boundary_path

    .. automethod:: pixel_boundary_path
    
    .. automethod:: boundary_path_wcs

    .. automethod:: transform

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3A2FF847-BE14-4AC5-9BD4-BD3DCAEF2281
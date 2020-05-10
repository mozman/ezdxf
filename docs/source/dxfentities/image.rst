Image
=====

.. module:: ezdxf.entities
    :noindex:

Add a raster IMAGE (`DXF Reference`_) to the DXF file, the file itself is not embedded into the DXF file, it is always a separated file.
The IMAGE entity is like a block reference, you can use it multiple times to add the image on different locations
with different scales and rotations. But therefore you need a also a IMAGEDEF entity, see :class:`ImageDef`.
`ezdxf` creates only images in the xy-plan, you can place images in the 3D space too, but then you have to set
the :attr:`Image.dxf.u_pixel` and the :attr:`Image.dxf.v_pixel` vectors by yourself.

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

        U-vector of a single pixel (points along the visual bottom of the image, starting at the insertion point)
        as ``(x, y, z)`` tuple

    .. attribute:: dxf.v_pixel

        V-vector of a single pixel (points along the visual left side of the image, starting at the insertion point)
        as ``(x, y, z)`` tuple

    .. attribute:: dxf.image_size

        Image size in pixels as ``(x, y)`` tuple

    .. attribute:: dxf.image_def_handle

        Handle to the image definition entity, see :class:`ImageDef`

    .. attribute:: dxf.flags

        =================================== ======= ===========
        :attr:`Image.dxf.flags`             Value   Description
        =================================== ======= ===========
        :attr:`Image.SHOW_IMAGE`            1       Show image
        :attr:`Image.SHOW_WHEN_NOT_ALIGNED` 2       Show image when not aligned with screen
        :attr:`Image.USE_CLIPPING_BOUNDARY` 4       Use clipping boundary
        :attr:`Image.USE_TRANSPARENCY`      8       Transparency is on
        =================================== ======= ===========

    .. attribute:: dxf.clipping

        Clipping state:

        ===== ============
        ``0`` clipping off
        ``1`` clipping on
        ===== ============

    .. attribute:: dxf.brightness

        Brightness value (0-100; default = ``50``)

    .. attribute:: dxf.contrast

        Contrast value (0-100; default = ``50``)

    .. attribute:: dxf.fade

        Fade value (0-100; default = ``0``)

    .. attribute:: dxf.clipping_boundary_type

        Clipping boundary type:

        === ============
        1   Rectangular
        2   Polygonal
        === ============

    .. attribute:: dxf.count_boundary_points

        Number of clip boundary vertices, maintained by `ezdxf`.

    .. attribute:: Image.dxf.clip_mode

        Clip mode (DXF R2010):

        === ========
        0   Outside
        1   Inside
        === ========

    .. autoattribute:: boundary_path

    .. automethod:: reset_boundary_path

    .. automethod:: set_boundary_path

    .. automethod:: get_image_def() -> ImageDef

    .. automethod:: transform(m: Matrix44) -> Image

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3A2FF847-BE14-4AC5-9BD4-BD3DCAEF2281
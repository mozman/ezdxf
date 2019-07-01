Underlay
========

.. module:: ezdxf.entities

UNDERLAY entity (`DXF Reference`_) links an underlay file to the DXF file, the file itself is not embedded into the
DXF file, it is always a separated file. The (PDF)UNDERLAY entity is like a block reference, you can use it
multiple times to add the underlay on different locations with different scales and rotations. But therefore
you need a also a (PDF)DEFINITION entity, see :class:`UnderlayDefinition`.

The DXF standard supports three different file formats: PDF, DWF (DWFx) and DGN. An Underlay can be clipped by a
rectangle or a polygon path. The clipping coordinates are 2D :ref:`OCS` coordinates in drawing units but
without scaling.

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3EC8FBCC-A85A-4B0B-93CD-C6C785959077

PdfUnderlay
-----------

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'PDFUNDERLAY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_underlay`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. class:: PdfUnderlay

    .. attribute:: dxf.insert

        Insertion point, lower left corner of the image in :ref:`OCS`.

    .. attribute:: dxf.scale_x

        Scaling factor in x-direction (float)

    .. attribute:: dxf.scale_y

        Scaling factor in y-direction (float)

    .. attribute:: dxf.scale_z

        Scaling factor in z-direction (float)

    .. attribute:: dxf.rotation

        ccw rotation in degrees around the extrusion vector (float)

    .. attribute:: dxf.extrusion

        extrusion vector, default = ``(0, 0, 1)``

    .. attribute:: dxf.underlay_def

        Handle to the underlay definition entity, see :class:`UnderlayDefinition`

    .. attribute:: dxf.flags

        ============================== ======= ===========
        :attr:`dxf.flags`              Value   Description
        ============================== ======= ===========
        UNDERLAY_CLIPPING              1       clipping is on/off
        UNDERLAY_ON                    2       underlay is on/off
        UNDERLAY_MONOCHROME            4       Monochrome
        UNDERLAY_ADJUST_FOR_BACKGROUND 8       Adjust for background
        ============================== ======= ===========

    .. attribute:: dxf.contrast

        Contrast value (``20`` - ``100``; default = ``100``)

    .. attribute:: dxf.fade

        Fade value (``0`` - ``80``; default = ``0``)


    .. attribute:: clipping

        ``True`` or ``False`` (read/write)

    .. attribute:: on

        ``True`` or ``False`` (read/write)

    .. attribute:: monochrome

        ``True`` or ``False`` (read/write)

    .. attribute:: adjust_for_background

        ``True`` or ``False`` (read/write)

    .. attribute:: scale

        Scaling ``(x, y, z)`` tuple (read/write)

    .. attribute:: boundary_path

        Boundary path as list of vertices (read/write).

        Two vertices describe a rectangle (lower left and upper right corner), more than two vertices
        is a polygon as clipping path.

    .. attribute:: underlay_def

        Associated (PDF)DEFINITION entity. see :class:`UnderlayDefinition`.

    .. automethod:: reset_boundary_path()


DwfUnderlay
-----------

======================== ==========================================
Subclass of              :class:`ezdxf.entities.PdfUnderlay`
DXF type                 ``'DWFUNDERLAY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_underlay`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. class:: DwfUnderlay

DgnUnderlay
-----------

======================== ==========================================
Subclass of              :class:`ezdxf.entities.PdfUnderlay`
DXF type                 ``'DGNUNDERLAY'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_underlay`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. class:: DgnUnderlay

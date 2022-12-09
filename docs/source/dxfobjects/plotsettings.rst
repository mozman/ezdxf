PlotSettings
============

.. module:: ezdxf.entities
    :noindex:

All `PLOTSETTINGS`_ attributes are part of the :class:`~ezdxf.entities.DXFLayout`
entity, I don't know if this entity also appears as standalone entity.

======================== ===========================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'PLOTSETTINGS'``
Factory function         internal data structure
======================== ===========================================================

.. _PLOTSETTINGS: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-1113675E-AB07-4567-801A-310CDE0D56E9


.. class:: PlotSettings

    .. attribute:: dxf.page_setup_name

        default is ""

    .. attribute:: dxf.plot_configuration_file

        default is "Adobe PDF"

    .. attribute:: dxf.paper_size

        default is "A3"

    .. attribute:: dxf.plot_view_name

        default is ""

    .. attribute:: dxf.left_margin

        default is 7.5 mm

    .. attribute:: dxf.bottom_margin

        default is 20 mm

    .. attribute:: dxf.right_margin

        default is 7.5 mm

    .. attribute:: dxf.top_margin

        default is 20 mm

    .. attribute:: dxf.paper_width

        default is 420 mm

    .. attribute:: dxf.paper_height

        default is 297 mm

    .. attribute:: dxf.plot_origin_x_offset

        default is 0

    .. attribute:: dxf.plot_origin_y_offset

        default is 0

    .. attribute:: dxf.plot_window_x1

        default is 0

    .. attribute:: dxf.plot_window_y1

        default is 0

    .. attribute:: dxf.plot_window_x2

        default is 0

    .. attribute:: dxf.plot_window_y2

        default is 0

    .. attribute:: dxf.scale_numerator

        default is 1

    .. attribute:: dxf.scale_denominator

        default is 1

    .. attribute:: dxf.plot_layout_flags

        ======= ======================================
        1       plot viewport borders
        2       show plot-styles
        4       plot centered
        8       plot hidden == hide paperspace entities?
        16      use standard scale
        32      plot with plot-styles
        64      scale lineweights
        128     plot entity lineweights
        512     draw viewports first
        1024    model type
        2048    update paper
        4096    zoom to paper on update
        8192    initializing
        16384   prev plot-init
        ======= ======================================

        default is 688

    .. attribute:: dxf.plot_paper_units

        === =====================
        0   Plot in inches
        1   Plot in millimeters
        2   Plot in pixels
        === =====================

    .. attribute:: dxf.plot_rotation

        === =============================
        0   No rotation
        1   90 degrees counterclockwise
        2   Upside-down
        3   90 degrees clockwise
        === =============================

    .. attribute:: dxf.plot_type

        === =============================
        0   Last screen display
        1   Drawing extents
        2   Drawing limits
        3   View specified by code 6
        4   Window specified by codes 48, 49, 140, and 141
        5   Layout information
        === =============================

    .. attribute:: dxf.current_style_sheet

        default is ""

    .. attribute:: dxf.standard_scale_type

        === =============================
        0   Scaled to Fit
        1   1/128"=1'
        2   1/64"=1'
        3   1/32"=1'
        4   1/16"=1'
        5   3/32"=1'
        6   1/8"=1'
        7   3/16"=1'
        8   1/4"=1'
        9   3/8"=1'
        10  1/2"=1'
        11  3/4"=1'
        12  1"=1'
        13  3"=1'
        14  6"=1'
        15  1'=1'
        16  1:1
        17  1:2
        18  1:4
        19  1:8
        20  1:10
        21  1:16
        22  1:20
        23  1:30
        24  1:40
        25  1:50
        26  1:100
        27  2:1
        28  4:1
        29  8:1
        30  10:1
        31  100:1
        32  1000:1
        === =============================

    .. attribute:: dxf.shade_plot_mode

        === =============================
        0   As Displayed
        1   Wireframe
        2   Hidden
        3   Rendered
        === =============================

    .. attribute:: dxf.shade_plot_resolution_level

        === =============================
        0   Draft
        1   Preview
        2   Normal
        3   Presentation
        4   Maximum
        5   Custom
        === =============================

    .. attribute:: dxf.shade_plot_custom_dpi

        default is 300

    .. attribute:: dxf.unit_factor

        default is 1

    .. attribute:: dxf.paper_image_origin_x

        default is 0

    .. attribute:: dxf.paper_image_origin_y

        default is 0

    .. attribute:: dxf.shade_plot_handle

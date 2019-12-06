Dimension
=========

.. module:: ezdxf.entities
    :noindex:

The DIMENSION entity (`DXF Reference`_) represents several types of dimensions in many orientations and alignments.
The basic types of dimensioning are linear, radial, angular, ordinate, and arc length.

For more information about dimensions see the online help from AutoDesk: `About the Types of Dimensions`_

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'DIMENSION'``
factory function         see table below
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

Factory Functions
-----------------

=========================================== ==========================================
`Linear and Rotated Dimension (DXF)`_       :meth:`~ezdxf.layouts.BaseLayout.add_linear_dim`
`Aligned Dimension (DXF)`_                  :meth:`~ezdxf.layouts.BaseLayout.add_aligned_dim`
`Angular Dimension (DXF)`_                  :meth:`~ezdxf.layouts.BaseLayout.add_angular_dim`
`Angular 3P Dimension (DXF)`_               :meth:`~ezdxf.layouts.BaseLayout.add_angular_3p_dim`
`Diameter Dimension (DXF)`_                 :meth:`~ezdxf.layouts.BaseLayout.add_diameter_dim`
`Radius Dimension (DXF)`_                   :meth:`~ezdxf.layouts.BaseLayout.add_radius_dim`
`Ordinate Dimension (DXF)`_                 :meth:`~ezdxf.layouts.BaseLayout.add_ordinate_dim`
=========================================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Dimension

    There is only one :class:`Dimension` class to represent all different dimension types.

    .. attribute:: dxf.version

        Version number: ``0`` = R2010. (int, DXF R2010)

    .. attribute:: dxf.geometry

        Name of the BLOCK that contains the entities that make up the dimension picture.

        For AutoCAD this graphical representation is mandatory, else AutoCAD will not open the
        DXF drawing. BricsCAD will render the DIMENSION entity by itself, if the graphical representation is
        not present, but uses the BLOCK instead of rendering, if it is present.

    .. attribute:: dxf.dimstyle

        Dimension style (:class:`DimStyle`) name as string.

    .. attribute:: dxf.dimtype

        Values 0-6 are integer values that represent the dimension type. Values 32, 64, and 128 are bit values, which
        are added to the integer values.

        === ===================================================================
        0   `Linear and Rotated Dimension (DXF)`_
        1   `Aligned Dimension (DXF)`_
        2   `Angular Dimension (DXF)`_
        3   `Diameter Dimension (DXF)`_
        4   `Radius Dimension (DXF)`_
        5   `Angular 3P Dimension (DXF)`_
        6   `Ordinate Dimension (DXF)`_
        32  Indicates that graphical representation :attr:`geometry` is referenced by this dimension only.
            (always set in DXF R13 and later)
        64  Ordinate type. This is a bit value (bit 7) used only with integer value 6. If set, ordinate is `X-type`;
            if not set, ordinate is `Y-type`
        128 This is a bit value (bit 8) added to the other :attr:`dimtype` values if the dimension text has been
            positioned at a user-defined location rather than at the default location
        === ===================================================================

    .. attribute:: dxf.defpoint

        Definition point for all dimension types. (3D Point in :ref:`WCS`)

        Linear and rotated dimension: :attr:`dxf.defpoint` specifies the dimension line location.

        Arc and angular dimension: :attr:`dxf.defpoint` and :attr:`dxfdefpoint4` specify the endpoints of the
        line used to determine the second extension line.

    .. attribute:: dxf.defpoint2

        Definition point for linear and angular dimensions. (3D Point in :ref:`WCS`)

        Linear and rotated dimension: The :attr:`dxf.defpoint2` specifies the start point of the first extension line.

        Arc and angular dimension: The :attr:`dxf.defpoint2` and :attr:`dxf.defpoint3` specify the endpoints of the
        line used to determine the first extension line.

    .. attribute:: dxf.defpoint3

        Definition point for linear and angular dimensions. (3D Point in :ref:`WCS`)

        Linear and rotated dimension: The :attr:`dxf.defpoint3` specifies the start point of the second extension line.

        Arc and angular dimension: The :attr:`dxf.defpoint2` and :attr:`dxf.defpoint3` specify the endpoints of the
        line used to determine the first extension line.

    .. attribute:: dxf.defpoint4

        Definition point for diameter, radius, and angular dimensions. (3D Point in :ref:`WCS`)

        Arc and angular dimension: :attr:`dxf.defpoint` and :attr:`dxf.defpoint4` specify the endpoints of the
        line used to determine the second extension line.

    .. attribute:: dxf.defpoint5

        Point defining dimension arc for angular dimensions, specifies the location of the dimension line arc.
        (3D Point in :ref:`OCS`)

    .. attribute:: dxf.angle

        Angle of linear and rotated dimensions in degrees. (float)

    .. attribute:: dxf.leader_length

        Leader length for radius and diameter dimensions. (float)

    .. attribute:: dxf.text_midpoint

        Middle point of dimension text. (3D Point in :ref:`OCS`)

    .. attribute:: dxf.insert

        Insertion point for clones of a linear dimensions—Baseline and Continue. (3D Point in :ref:`OCS`)

        This value is used by CAD application (Baseline and Continue) and ignored by `ezdxf`.

    .. attribute:: dxf.attachment_point

        Text attachment point (int, DXF R2000), default value is ``5``.

        === ================
        1   Top left
        2   Top center
        3   Top right
        4   Middle left
        5   Middle center
        6   Middle right
        7   Bottom left
        8   Bottom center
        9   Bottom right
        === ================

    .. attribute:: dxf.line_spacing_style

        Dimension text line-spacing style (int, DXF R2000), default value is ``1``.

        === ============================================
        1   At least (taller characters will override)
        2   Exact (taller characters will not override)
        === ============================================

    .. attribute:: dxf.line_spacing_factor

        Dimension text-line spacing factor. (float, DXF R2000)

        Percentage of default (3-on-5) line spacing to be applied. Valid values range from ``0.25`` to ``4.00``.

    .. attribute:: dxf.actual_measurement

        Actual measurement (float, DXF R2000), this is an optional attribute and often not present. (read-only value)

    .. attribute:: dxf.text

        Dimension text explicitly entered by the user (str), default value is an empty string.

        If empty string or ``'<>'``, the dimension measurement is drawn as the text,
        if ``' '`` (one blank space), the text is suppressed. Anything else is drawn as the text.

    .. attribute:: dxf.oblique_angle

        Linear dimension types with an oblique angle have an optional :attr:`dxf.oblique_angle`.

        When added to the rotation :attr:`dxf.angle` of the linear dimension, it gives the angle of the extension lines.

    .. attribute:: dxf.text_rotation

        Defines is the rotation angle of the dimension text away from its default orientation
        (the direction of the dimension line). (float)

    .. attribute:: dxf.horizontal_direction

        Indicates the horizontal direction for the dimension entity (float).

        This attribute determines the orientation of dimension text and lines for horizontal, vertical, and
        rotated linear dimensions. This value is the negative of the angle in the OCS xy-plane between the dimension
        line and the OCS x-axis.

    .. autoattribute:: dimtype

    .. automethod:: get_dim_style

    .. automethod:: get_geometry_block

    .. automethod:: get_measurement

DimStyleOverride
----------------

All of the :class:`DimStyle` attributes can be overridden for each :class:`Dimension` entity individually.

The :class:`DimStyleOverride` class manages all the complex dependencies between :class:`DimStyle` and
:class:`Dimension`, the different features of all DXF versions and the rendering process to create the
:class:`Dimension` picture as BLOCK, which is required for AutoCAD.

.. class:: DimStyleOverride

    .. attribute:: dimension

        Base :class:`Dimension` entity.

    .. attribute:: dimstyle

        By :attr:`dimension` referenced :class:`DimStyle` entity.

    .. attribute:: dimstyle_attribs

        Contains all overridden attributes of :attr:`dimension`, as a ``dict`` with :class:`DimStyle` attribute names
        as keys.

    .. automethod:: __getitem__

    .. automethod:: __setitem__

    .. automethod:: __delitem__

    .. automethod:: get

    .. automethod:: pop

    .. automethod:: update

    .. automethod:: commit

    .. automethod:: get_arrow_names

    .. automethod:: set_arrows

    .. automethod:: set_tick

    .. automethod:: set_text_align

    .. automethod:: set_tolerance

    .. automethod:: set_limits

    .. automethod:: set_text_format

    .. automethod:: set_dimline_format

    .. automethod:: set_extline_format

    .. automethod:: set_extline1

    .. automethod:: set_extline2

    .. automethod:: set_text

    .. automethod:: shift_text

    .. automethod:: set_location

    .. automethod:: user_location_override

    .. automethod:: render

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-239A1BDD-7459-4BB9-8DD7-08EC79BF1EB0

.. _About the Types of Dimensions: https://knowledge.autodesk.com/support/autocad/getting-started/caas/CloudHelp/cloudhelp/2020/ENU/AutoCAD-Core/files/GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0-htm.html

.. _Aligned Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-7A123D5D-AC98-4A9A-A8CF-1A7EF5030418

.. _Angular Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-09821B78-9F8E-43BA-82F2-8C931485EDC9

.. _Angular 3P Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-09821B78-9F8E-43BA-82F2-8C931485EDC9

.. _Linear and Rotated Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-F0004556-493C-48D5-8619-61D6ADF05C04

.. _Ordinate Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72F01288-0D63-43E8-8179-8CE3BA544C40

.. _Radius Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-165A992D-9017-4C1E-B8CC-E70A17191BFE

.. _Diameter Dimension (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-165A992D-9017-4C1E-B8CC-E70A17191BFE

.. _Dimension Style Overrides (DXF): http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-6A4C31C0-4988-499C-B5A4-15582E433B0F

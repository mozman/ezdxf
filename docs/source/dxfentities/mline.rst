MLine
=====

.. module:: ezdxf.entities
    :noindex:

The MLINE entity (`DXF Reference`_).


======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'MLINE'``
factory function         :meth:`~ezdxf.layouts.BaseLayout.add_mline`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-590E8AE3-C6D9-4641-8485-D7B3693E432C

.. class:: MLine

    .. attribute:: dxf.style_name

        :class:`MLineStyle` name stored in :attr:`Drawing.mline_styles`
        dictionary, use :meth:`~MLine.set_style` to change the MLINESTYLE
        and update geometry accordingly.

    .. attribute:: dxf.style_handle

        Handle of :class:`MLineStyle`, use :meth:`~MLine.set_style` to change
        the MLINESTYLE and update geometry accordingly.

    .. attribute:: dxf.scale_factor

        MLINE scaling factor, use method :meth:`~MLine.set_scale_factor`
        to change the scaling factor and update geometry accordingly.

    .. attribute:: dxf.justification

        Justification defines the location of the MLINE in relation to
        the reference line, use method :meth:`~MLine.set_justification`
        to change the justification and update geometry accordingly.

        Constants defined in :mod:`ezdxf.lldxf.const`:

        ============================== =======
        dxf.justification              Value
        ============================== =======
        MLINE_TOP                      0
        MLINE_ZERO                     1
        MLINE_BOTTOM                   2
        MLINE_RIGHT (alias)            0
        MLINE_CENTER (alias)           1
        MLINE_LEFT (alias)             2
        ============================== =======

    .. attribute:: dxf.flags

        Use method :meth:`~MLine.close` and the properties :attr:`~MLine.start_caps`
        and :attr:`~MLine.end_caps` to change these flags.

        Constants defined in :mod:`ezdxf.lldxf.const`:

        ============================== =======
        dxf.flags                      Value
        ============================== =======
        MLINE_HAS_VERTEX               1
        MLINE_CLOSED                   2
        MLINE_SUPPRESS_START_CAPS      4
        MLINE_SUPPRESS_END_CAPS        8
        ============================== =======

    .. attribute:: dxf.start_location

        Start location of the reference line. (read only)

    .. attribute:: dxf.count

        Count of MLINE vertices. (read only)

    .. attribute:: dxf.style_element_count

        Count of elements in :class:`MLineStyle` definition. (read only)

    .. attribute:: dxf.extrusion

        Normal vector of the entity plane, but MLINE is not an OCS entity, all
        vertices of the reference line are WCS! (read only)

    .. attribute:: vertices

        MLINE vertices as :class:`MLineVertex` objects, stored in a
        regular Python list.

    .. autoproperty:: style

    .. automethod:: set_style

    .. automethod:: set_scale_factor

    .. automethod:: set_justification

    .. autoproperty:: is_closed

    .. automethod:: close

    .. autoproperty:: start_caps

    .. autoproperty:: end_caps

    .. automethod:: __len__

    .. automethod:: start_location() -> Vec3

    .. automethod:: get_locations() -> List[Vec3]

    .. automethod:: extend(vertices: Iterable[Vec3]) -> None

    .. automethod:: clear

    .. automethod:: update_geometry

    .. automethod:: generate_geometry

    .. automethod:: transform(m: Matrix44) -> MLine

    .. automethod:: virtual_entities() -> Iterable[DXFGraphic]

    .. automethod:: explode(target_layout: BaseLayout = None) -> EntityQuery

.. class:: MLineVertex

    .. attribute:: location

        Reference line vertex location.

    .. attribute:: line_direction

        Reference line direction.

    .. attribute:: miter_direction

    .. attribute:: line_params

        The line parameterization is a list of float values. The list may
        contain zero or more items.

        The first value (miter-offset) is the distance from the vertex
        :attr:`location` along the :attr:`miter_direction` vector to the
        point where the line element's path intersects the miter vector.

        The next value (line-start-offset) is the distance along the
        :attr:`line_direction` from the miter/line path intersection point to
        the actual start of the line element.

        The next value (dash-length) is the distance from the start of the
        line element (dash) to the first break (gap) in the line element.
        The successive values continue to list the start and stop points of
        the line element in this segment of the mline.

    .. attribute:: fill_params

        The fill parameterization is also a list of float values.
        Similar to the line parameterization, it describes the
        parameterization of the fill area for this mline segment.
        The values are interpreted identically to the line parameters and when
        taken as a whole for all line elements in the mline segment, they
        define the boundary of the fill area for the mline segment.

.. class:: MLineStyle

    The :class:`MLineStyle` stores the style properties for the MLINE entity.

    .. attribute:: dxf.name

    .. attribute:: dxf.description

    .. attribute:: dxf.flags

    .. attribute:: dxf.fill_color

        :ref:`ACI` value of the fill color

    .. attribute:: dxf.start_angle

    .. attribute:: dxf.end_angle

    .. attribute:: elements

        :class:`~ezdxf.entities.mline.MLineStyleElements` object

    .. automethod:: update_all

.. class:: ezdxf.entities.mline.MLineStyleElements

    .. attribute:: elements

        List of :class:`~ezdxf.entities.mline.MLineStyleElement` objects, one
        for each line element.

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: append

.. class:: ezdxf.entities.mline.MLineStyleElement

    Named tuple to store properties of a line element.

    .. attribute:: offset

        Normal offset from the reference line: if justification is ``MLINE_ZERO``,
        positive values are above and negative values are below the reference
        line.

    .. attribute:: color

        :ref:`ACI` value

    .. attribute:: linetype

        Linetype name
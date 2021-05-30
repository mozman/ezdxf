MPolygon
========

.. module:: ezdxf.entities
    :noindex:

The MPOLYGON entity is not a core DXF entity and is not supported by every CAD
application or DXF library.

The :class:`MPolygon` class is very similar to the :class:`Hatch` class with
small differences in supported DXF attributes and features.

The boundary paths of the MPOLYGON are visible and use the graphical DXF
attributes of the main entity like :attr:`dxf.color`, :attr:`dxf.linetype` and so on.
The solid filling is only visible if the attribute :attr:`dxf.solid_fill` is 1,
the color of the solid fill is defined by :attr:`dxf.fill_color` as :ref:`ACI`.

The MPOLYGON does not support associated source path entities, because the
MPOLYGON also represents the boundary paths as visible graphical objects.

Hatch patterns are supported, but the hatch style tag is not supported, the
default hatch style is :attr:`ezdxf.const.HATCH_STYLE_NESTED` and the style
flags of the boundary paths are ignored.

Background color for pattern fillings is supported, set background color
by property :attr:`MPolygon.bgcolor` as RGB tuple.

An example for edge paths as boundary paths is not available or edge paths
are not supported. `Ezdxf` does not export MPOLYGON entities with edge paths!

.. seealso::
    For more information see the :class:`ezdxf.entities.Hatch` documentation.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'MPOLYGON'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_mpolygon`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. class:: MPolygon

    .. attribute:: dxf.pattern_name

        Pattern name as string

    .. attribute:: dxf.solid_fill

        === ==========================================================
        1   solid fill, better use: :meth:`MPolygon.set_solid_fill`
        0   pattern fill, better use: :meth:`MPolygon.set_pattern_fill`
        === ==========================================================

    .. attribute:: dxf.hatch_style

        === ========
        0   normal
        1   outer
        2   ignore
        === ========

        (search AutoCAD help for more information)

    .. attribute:: dxf.pattern_type

        === ===================
        0   user
        1   predefined
        2   custom
        === ===================

    .. attribute:: dxf.pattern_angle

        Actual pattern angle in degrees (float). Changing this value does not
        rotate the pattern, use :meth:`~MPolygon.set_pattern_angle` for this task.

    .. attribute:: dxf.pattern_scale

        Actual pattern scaling factor (float). Changing this value does not
        scale the pattern use :meth:`~MPolygon.set_pattern_scale` for this task.

    .. attribute:: dxf.pattern_double

        1 = double pattern size else 0. (int)

    .. attribute:: dxf.elevation

       Z value represents the elevation height of the :ref:`OCS`. (float)

    .. attribute:: paths

        :class:`BoundaryPaths` object.

    .. attribute:: pattern

        :class:`Pattern` object.

    .. attribute:: gradient

        :class:`Gradient` object.

    .. autoproperty:: has_solid_fill

    .. autoproperty:: has_pattern_fill

    .. autoproperty:: has_gradient_data

    .. autoproperty:: bgcolor

    .. automethod:: set_pattern_definition

    .. automethod:: set_pattern_scale

    .. automethod:: set_pattern_angle

    .. automethod:: set_solid_fill

    .. automethod:: set_pattern_fill

    .. automethod:: set_gradient

    .. automethod:: transform(m: Matrix44) -> MPolygon


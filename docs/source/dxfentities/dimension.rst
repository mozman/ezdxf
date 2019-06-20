Dimension
=========

.. class:: Dimension(GraphicEntity)

    todo

Create dimensions in layouts and blocks by following factory functions

    - :meth:`~ezdxf.modern.layouts.Layout.add_linear_dim`
    - :meth:`~ezdxf.modern.layouts.Layout.add_aligned_dim`
    - :meth:`~ezdxf.modern.layouts.Layout.add_angular_dim`
    - :meth:`~ezdxf.modern.layouts.Layout.add_diameter_dim`
    - :meth:`~ezdxf.modern.layouts.Layout.add_radial_dim`
    - :meth:`~ezdxf.modern.layouts.Layout.add_angular_3p_dim`
    - :meth:`~ezdxf.modern.layouts.Layout.add_ordinate_dim`


DXF Attributes for Dimension
----------------------------

:ref:`Common graphical DXF attributes`

.. attribute:: Line.dxf.defpoint

    Definition point for all dimension types (WCS or UCS)


DimStyleOverride
----------------

All of the :class:`DimStyle` attributes can be overridden for each :class:`Dimension` entity individually, for this
functionality exists this special :class:`DimStyleOverride` class.

The :class:`DimStyleOverride` class manages all the complex dependencies between :class:`DimStyle`, :class:`Dimension`,
the different features for all DXF versions and the rendering process, which is required for AutoCAD. And therefore all
the convenience function for a more easy dimension handling are also located this class.

.. class:: DimStyleOverride

    todo

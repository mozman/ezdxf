.. _tut_linear_dimension:

Tutorial for Linear Dimensions
==============================

The :class:`~ezdxf.entities.Dimension` entity is the generic entity for all dimension types, but unfortunately
AutoCAD is **not willing** to show a dimension line defined only by this dimension entity, it also needs an
anonymous block which contains the dimension line shape constructed by basic DXF entities like LINE and TEXT
entities, this representation is called the dimension line `rendering` in this documentation, beside the fact
this is not a real graphical rendering. BricsCAD is a much more friendly CAD application, which do show the
dimension entity without the graphical rendering as block, which was very useful for testing, because there is no
documentation how to apply all the dimension style variables (more than 80).
This seems to be the reason why dimension lines are rendered so differently by many CAD application.

Don't expect to get the same rendering results by `ezdxf` as you get from AutoCAD, `ezdxf` tries
to be as close to the results rendered by BricsCAD, but it was not possible to implement all
the various combinations of dimension style parameters.

Text rendering is another problem, because `ezdxf` has no real rendering engine. Some font properties, like the real
text width, are not available to `ezdxf` and may also vary slightly for different CAD applications.
The text properties in `ezdxf` are based on the default monospaced standard font, but for TrueType fonts the space
around the text is much bigger than needed.

Horizontal Dimension
--------------------

.. code-block:: Python

    import ezdxf

    # Argument setup=True setups the default dimension styles
    doc = ezdxf.new('R2010', setup=True)

    # Add new dimension entities to the modelspace
    msp = doc.modelspace()
    # Add a LINE entity, not required
    msp.add_line((0, 0), (3, 0))
    # Add a horizontal dimension, default dimension style is 'EZDXF'
    dim = msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0))
    # Necessary second step, to create the BLOCK entity with the dimension geometry.
    # Additional processing of the dimension line could happen between adding and
    # rendering call.
    dim.render()
    doc.saveas('dim_linear_horiz.dxf')

.. image:: gfx/dim_linear_horiz.png


The example above creates a horizontal :class:`~ezdxf.entities.Dimension` entity, the default dimension style
``'EZDXF'`` and is defined as 1 drawing unit is 1m in reality, the drawing scale 1:100 and the length factor is 100,
which creates a measurement text in cm.

The `base` point defines the location of the dimension line, `ezdxf` accepts any point on the dimension line,
the point `p1` defines the start point of the first extension line, which also defines the first measurement point
and the point `p2` defines the start point of the second extension line, which also defines the second
measurement point.

The return value `dim` is **not** a dimension entity, instead a :class:`~ezdxf.entities.DimStyleOverride` object is
returned, the dimension entity is stored as `dim.dimension`.

Vertical and Rotated Dimension
------------------------------

Argument `angle` defines the angle of the dimension line in relation to the x-axis of the WCS or UCS, measurement
is the distance between first and second measurement point in direction of `angle`.

.. code-block:: Python

    # assignment to dim is not necessary, if no additional processing happens
    msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0), angle=-30).render()
    doc.saveas('dim_linear_rotated.dxf')

.. image:: gfx/dim_linear_rotated.png

For a vertical dimension set argument `angle` to 90 degree, but in this example the vertical distance would be 0.

Aligned Dimension
-----------------

An aligned dimension line is parallel to the line defined by the definition points `p1` and `p2`. The placement of the
dimension line is defined by the argument `distance`, which is the distance between the definition line and the
dimension line. The `distance` of the dimension line is orthogonal to the base line in counter clockwise orientation.

.. code-block:: Python

    msp.add_line((0, 2), (3, 0))
    dim = msp.add_aligned_dim(p1=(0, 2), p2=(3, 0), distance=1)
    doc.saveas('dim_linear_aligned.dxf')

.. image:: gfx/dim_linear_aligned.png

Dimension Style Override
------------------------

Many dimension styling options are defined by the associated :class:`~ezdxf.entities.DimStyle` entity.
But often you wanna change just a few settings without creating a new dimension style, therefore the
DXF format has a protocol to store this changed settings in the dimension entity itself.
This protocol is supported by `ezdxf` and every factory function which creates dimension
entities supports the `override` argument.
This `override` argument is a simple Python dictionary
(e.g. :code:`override = {'dimtad': 4}`, place measurement text below dimension line).

The overriding protocol is managed by the :class:`~ezdxf.entities.DimStyleOverride` object,
which is returned by the most dimension factory functions.

Placing Measurement Text
------------------------

The "default" location of the measurement text depends on various :class:`~ezdxf.entities.DimStyle` parameters and is
applied if no user defined text location is defined.

Default Text Locations
~~~~~~~~~~~~~~~~~~~~~~

"Horizontal direction" means in direction of the dimension line and "vertical direction" means perpendicular to the
dimension line direction.

The **"horizontal"** location of the measurement text is defined by :attr:`~ezdxf.entities.DimStyle.dxf.dimjust`:

=== =====
0   Center of dimension line
1   Left side of the dimension line, near first extension line
2   Right side of the dimension line, near second extension line
3   Over first extension line
4   Over second extension line
=== =====

.. code-block:: Python

    msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0), override={'dimjust': 1}).render()

.. image:: gfx/dim_linear_dimjust.png

The **"vertical"** location of the measurement text relative to the dimension line is defined by
:attr:`~ezdxf.entities.DimStyle.dxf.dimtad`:

=== =====
0   Center, it is possible to adjust the vertical location by :attr:`~ezdxf.entities.DimStyle.dxf.dimtvp`
1   Above
2   Outside, handled like `Above` by `ezdxf`
3   JIS, handled like `Above` by `ezdxf`
4   Below
=== =====

.. code-block:: Python

    msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0), override={'dimtad': 4}).render()

.. image:: gfx/dim_linear_dimtad.png

The distance between text and dimension line is defined by :attr:`~ezdxf.entities.DimStyle.dxf.dimgap`.

The :class:`~ezdxf.entities.DimStyleOverride` object has a method :meth:`~ezdxf.entities.DimStyleOverride.set_text_align`
to set the default text location in an easy way, this is also the reason for the 2 step creation process of
dimension entities:

.. code-block:: Python

    dim = msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0))
    dim.set_text_align(halign='left', valign='center')
    dim.render()

====== =====
halign ``'left'``, ``'right'``, ``'center'``, ``'above1'``, ``'above2'``
valign ``'above'``, ``'center'``, ``'below'``
====== =====

Run function :func:`example_for_all_text_placings_R2007` in the example script `dimension_linear.py`_
to create a DXF file with all text placings supported by `ezdxf`.


User Defined Text Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beside the default location, it is possible to locate the measurement text freely.

Location Relative to Origin
+++++++++++++++++++++++++++

The user defined text location can be set by the argument `location` in most dimension factory functions and
always references the midpoint of the measurement text:

.. code-block:: Python

    msp.add_linear_dim(base=(3, 2), p1=(3, 0), p2=(6, 0), location=(4, 4)).render()

.. image:: gfx/dim_linear_user_location_absolute.png

The `location` is relative to origin of the active coordinate system or WCS if no UCS is defined in the
:meth:`~ezdxf.entities.DimStyleOverride.render` method, the user defined `location` can also be set by
:meth:`~ezdxf.entities.DimStyleOverride.user_location_override`.

Location Relative to Center of Dimension Line
+++++++++++++++++++++++++++++++++++++++++++++

The method :meth:`~ezdxf.entities.DimStyleOverride.set_location` has additional features for linear dimensions.
Argument `leader` = ``True`` adds a simple leader from the measurement text to the center of the dimension line and
argument `relative` = ``True`` places the measurement text relative to the center of the dimension line.

.. code-block:: Python

    dim = msp.add_linear_dim(base=(3, 2), p1=(3, 0), p2=(6, 0))
    dim.set_location(location=(-1, 1), leader=True, relative=True)
    dim.render()

.. image:: gfx/dim_linear_user_location_relative.png

Location Relative to Default Location
+++++++++++++++++++++++++++++++++++++

The method :meth:`~ezdxf.entities.DimStyleOverride.shift_text` shifts the measurement text away from the default text
location. Shifting directions are aligned to the text direction, which is the direction of the dimension line in most
cases, `dh` (for delta horizontal) shifts the text parallel to the text direction, `dv` (for delta vertical) shifts the
text perpendicular to the text direction. This method does not support leaders.

.. code-block:: Python

    dim = msp.add_linear_dim(base=(3, 2), p1=(3, 0), p2=(6, 0))
    dim.shift_text(dh=1, dv=1)
    dim.render()

.. image:: gfx/dim_linear_user_location_shift.png

.. _dimension_line_properties:

Dimension Line Properties
-------------------------

- Color
- Linetype
- Arrows
- Dimension Line Extension

TODO

.. _extension_line_properties:

Extension Line Properties
-------------------------

- Color
- Linetype
- Length

TODO

.. _overriding_measurement_text:

Overriding Measurement Text
---------------------------

TODO

.. _measurement_text_formatting_and_styling:

Measurement Text Formatting and Styling
---------------------------------------

- Decimal Places
- Decimal Point
- Rounding
- Zero Trimming
- Measurement Factor
- Text Color
- Background Filling

TODO

.. _tolerances_and_limits:

Tolerances and Limits
---------------------

TODO

Alternative Units
-----------------

Alternative units are not supported.


.. _dimension_linear.py:  https://github.com/mozman/ezdxf/blob/master/examples/render/dimension_linear.py
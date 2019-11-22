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

Text rendering is another problem, because `ezdxf` has no real rendering engine, font properties, like the real
text width, are not available to `ezdxf` and also my differ slightly for different CAD applications.
The text properties in `ezdxf` are based on the default monospaced standard font, but for true type fonts space
around the text is much bigger as needed.

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
``'EZDXF'`` is defined as 1 drawing unit is 1m in reality, drawing scale 1:100 and the length factor is 100, which
creates a measurement text in cm.

The `base` point defines the dimension line, `ezdxf` accepts any point on the dimension line, the point `p1` defines
the start point of the first extension line, which also defines the first measurement point and the point `p2`
defines the start point of the second extension line, which also defines the second measurement point.

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

TODO

Placing Measurement Text
------------------------

TODO

Default Text Locations
~~~~~~~~~~~~~~~~~~~~~~

TODO

User Defined Text Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

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


Definition Points Explained
---------------------------

TODO

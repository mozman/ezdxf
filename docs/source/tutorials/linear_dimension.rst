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

    # DXF R2010 drawing, official DXF version name: 'AC1024',
    # setup=True setups the default dimension styles
    doc = ezdxf.new('R2010', setup=True)

    msp = doc.modelspace()  # add new dimension entities to the modelspace
    msp.add_line((0, 0), (3, 0))  # add a LINE entity, not required
    # add a horizontal dimension
    dim = msp.add_linear_dim(base=(3, 2), p1=(0, 0), p2=(3, 0), dimstyle='EZDXF')
    # Necessary second step, to create the BLOCK entity with the dimension geometry.
    dim.render()
    doc.saveas('linear_dimension.dxf')

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

TODO

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

.. _overriding_measurement_text:

Overriding Measurement Text
---------------------------

TODO

.. _styling_measurement_text:

Styling Measurement Text
------------------------

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

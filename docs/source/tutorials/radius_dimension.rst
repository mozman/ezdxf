.. _tut_radius_dimension:

Tutorial for Radius Dimensions
==============================

Please read the :ref:`tut_linear_dimension` before, if you haven't.

.. code-block:: Python

    import ezdxf

    # DXF R2010 drawing, official DXF version name: 'AC1024',
    # setup=True setups the default dimension styles
    doc = ezdxf.new('R2010', setup=True)

    msp = doc.modelspace()  # add new dimension entities to the modelspace
    msp.add_circle((0, 0), radius=3)  # add a CIRCLE entity, not required
    # add default radius dimension, measurement text is located outside
    dim = msp.add_radius_dim(center=(0, 0), radius=3, angle=45, dimstyle='EZ_RADIUS')
    # necessary second step, to create the BLOCK entity with the dimension geometry.
    dim.render()
    doc.saveas('radius_dimension.dxf')

The example above creates a 45 degrees slanted radius :class:`~ezdxf.entities.Dimension` entity, the default dimension
style ``'EZ_RADIUS'`` is defined as 1 drawing unit is 1m in reality, drawing scale 1:100 and the length factor is 100, which
creates a measurement text in cm, the default location for the measurement text is outside of the circle.

The `center` point defines the the center of the circle but there doesn't have to exist a circle entity, `radius`
defines the circle radius, which is also the measurement, and angle defines the slope of the dimension line, it is also
possible to define the circle by a measurement point `mpoint` on the circle.

The return value `dim` is **not** a dimension entity, instead a :class:`~ezdxf.entities.DimStyleOverride` object is
returned, the dimension entity is stored as `dim.dimension`.

Placing Measurement Text
------------------------

TODO

Default Text Locations Inside
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

Default Text Locations Outside
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

User Defined Text Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

Overriding Measurement Text
---------------------------

See Linear Dimension Tutorial: :ref:`overriding_measurement_text`

Measurement Text Formatting and Styling
---------------------------------------

See Linear Dimension Tutorial: :ref:`measurement_text_formatting_and_styling`

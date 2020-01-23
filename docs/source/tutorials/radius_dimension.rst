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

There are different predefined DIMSTYLES to achieve various text placing locations.

DIMSTYLE ``'EZ_RADIUS'`` settings are: 1 drawing unit is 1m, scale 1:100, length_factor is 100 which creates
measurement text in cm, and a closed filled arrow with size 0.25 is used.

.. note::

    Not all possibles features of DIMSTYLE are supported and especially for radial dimension there are less
    features supported as for linear dimension because of the lack of good documentation.

.. seealso::

    - Graphical reference of many DIMVARS and some advanced information: :ref:`dimstyle_table_internals`
    - Source code file `standards.py`_ shows how to create your own DIMSTYLES.
    - `dimension_radius.py`_ for radius dimension examples.

Default Text Locations Outside
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``'EZ_RADIUS'`` default settings for to place text outside:

=========== ==============================================================================================
tmove       ``1`` to keep dim line with text, this is the best setting for text outside
            to preserve appearance of the DIMENSION entity, if editing afterwards in BricsCAD
            or AutoCAD.
dimtad      ``1`` to place text vertical above the dimension line
=========== ==============================================================================================

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, angle=45,
                             dimstyle='EZ_RADIUS'
                             )
    dim.render()  # required, but not shown in the following examples

.. image:: gfx/dim_radial_outside.png

To force text outside horizontal set :attr:`~ezdxf.entities.DimStyle.dxf.dimtoh` to ``1``:

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, angle=45,
                             dimstyle='EZ_RADIUS',
                             override={'dimtoh': 1}
                             )
.. image:: gfx/dim_radial_outside_horiz.png

Default Text Locations Inside
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DIMSTYLE ``'EZ_RADIUS_INSIDE'`` can be used to place the dimension text inside the circle at a default
location. Default DIMSTYLE settings are: 1 drawing unit is 1m, scale 1:100, length_factor is 100 which creates
measurement text in cm, and a closed filled arrow with size 0.25 is used.

``'EZ_RADIUS_INSIDE'`` default settings:

=========== ==============================================================================================
tmove       ``0`` to keep dim line with text, this is the best setting for text inside
            to preserve appearance of the DIMENSION entity, if editing afterwards in BricsCAD
            or AutoCAD.
dimtix      ``1`` to force text inside
dimatfit    ``0`` to force text inside, required by BricsCAD and AutoCAD
dimtad      ``0`` to center text vertical, BricsCAD and AutoCAD always create vertical centered text,
            `ezdxf` let you choose the vertical placement (above, below, center), but editing the
            DIMENSION in BricsCAD or AutoCAD will reset text to center placement.
=========== ==============================================================================================

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, angle=45,
                             dimstyle='EZ_RADIUS_INSIDE'
                             )

.. image:: gfx/dim_radial_inside_0.png

.. image:: gfx/dim_radial_inside_1.png

To force text inside horizontal set :attr:`~ezdxf.entities.DimStyle.dxf.dimtih` to ``1``:

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, angle=45,
                             dimstyle='EZ_RADIUS_INSIDE',
                             override={'dimtih': 1}
                             )

.. image:: gfx/dim_radial_inside_horiz.png


User Defined Text Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beside the default location it is always possible to override the text location by a user defined location. This
location also determines the angle of the dimension line and overrides the argument `angle`. For user defined locations
it is not necessary to force text inside (``dimtix=1``), because the location of the text is explicit given,
therefore the DIMSTYLE ``'EZ_RADIUS'`` can be used for all this examples.

User defined location outside of the circle:

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, location=(4, 4),
                             dimstyle='EZ_RADIUS'
                             )

.. image:: gfx/dim_radial_user_outside.png

User defined location outside of the circle and forced horizontal text:

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, location=(4, 4),
                             dimstyle='EZ_RADIUS',
                             override={'dimtoh': 1}
                             )

.. image:: gfx/dim_radial_user_outside_horiz.png

User defined location inside of the circle:

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, location=(1, 1),
                             dimstyle='EZ_RADIUS'
                             )

.. image:: gfx/dim_radial_user_inside_0.png

.. image:: gfx/dim_radial_user_inside_2.png

User defined location inside of the circle and forced horizontal text:

.. code-block:: python

    dim = msp.add_radius_dim(center=(0, 0), radius=2.5, location=(1, 1),
                             dimstyle='EZ_RADIUS',
                             override={'dimtih': 1},
                             )

.. image:: gfx/dim_radial_user_inside_horiz.png

Overriding Measurement Text
---------------------------

See Linear Dimension Tutorial: :ref:`tut_overriding_measurement_text`

Measurement Text Formatting and Styling
---------------------------------------

See Linear Dimension Tutorial: :ref:`tut_measurement_text_formatting_and_styling`


.. _dimension_radius.py:  https://github.com/mozman/ezdxf/blob/master/examples/render/dimension_radius.py
.. _standards.py: https://github.com/mozman/ezdxf/blob/master/src/ezdxf/tools/standards.py
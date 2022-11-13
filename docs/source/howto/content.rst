DXF Content
===========

General preconditions:

.. code-block:: python

    import sys
    import ezdxf

    try:
        doc = ezdxf.readfile("your_dxf_file.dxf")
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file.')
        sys.exit(2)
    msp = doc.modelspace()


.. _howto_get_color:

Get/Set Entity Color
--------------------

The entity color is stored as :term:`ACI` (AutoCAD Color Index):

.. code-block:: python

    aci = entity.dxf.color

Default value is 256 which means BYLAYER:

.. code-block:: python

    layer = doc.layers.get(entity.dxf.layer)
    aci = layer.get_color()

The special :meth:`~ezdxf.entities.Layer.get_color` method is required, because
the color attribute :attr:`Layer.dxf.color` is misused as layer on/off flag, a
negative color value means the layer is off.

ACI value 0 means BYBLOCK, which means the color from the block reference
(INSERT entity).

Set color as ACI value as int in range [0, 256]:

.. code-block:: python

    entity.dxf.color = 1


The ACI value 7 has a special meaning, it is white on dark backgrounds and white
on light backgrounds.

.. _howto_get_entity_rgb_color:

Get/Set Entity RGB Color
------------------------

RGB true color values are supported since DXF R13 (AC1012), the 24-bit RGB value
is stored as integer in the DXF attribute :attr:`~ezdxf.entities.DXFGraphic.dxf.true_color`:

.. code-block:: python

    # 24 bit binary value: 0bRRRRRRRRGGGGGGGGBBBBBBBB or hex value: 0xRRGGBB
    # set true color value to red
    entity.dxf.true_color = 0xFF0000

Use the helper functions from the :mod:`ezdxf.colors` module for
RGB integer value handling:

.. code-block:: python

    from ezdxf import colors

    entity.dxf.true_color = colors.rgb2int((0xFF, 0, 0))
    r, g, b = colors.int2rgb(entity.dxf.true_color)

The RGB values of the AutoCAD default colors are not officially documented,
but an accurate translation table is included in `ezdxf`:

.. code-block:: python

    # Warning: ACI value 256 (BYLAYER) raises an IndexError!
    rgb24 = colors.DXF_DEFAULT_COLORS[aci]
    print(f"RGB Hex Value: #{rgb24:06X}")
    r, g, b = colors.int2rgb(rgb24)
    print(f"RGB Channel Values: R={r:02X} G={g:02X} b={b:02X}")

If :attr:`color` and :attr:`true_color` values are set, BricsCAD and AutoCAD use
the :attr:`true_color` value as display color for the entity.

Get/Set True Color as RGB-Tuple
-------------------------------

Get/Set the true color value as (r, g, b)-tuple by the
:attr:`~ezdxf.entities.DXFGraphic.rgb` property of the
:class:`~ezdxf.entities.DXFGraphic` entity:

.. code-block:: python

    # set true color value to red
    entity.rgb = (0xFF, 0, 0)

    # get true color values
    r, g, b = entity.rgb

.. _howto_get_attribs:

Get/Set Block Reference Attributes
----------------------------------

Block references (:class:`~ezdxf.entities.Insert`) can have attached attributes (:class:`~ezdxf.entities.Attrib`),
these are simple text annotations with an associated tag appended to the block reference.

Iterate over all appended attributes:

.. code-block:: python

    # get all INSERT entities with entity.dxf.name == "Part12"
    blockrefs = msp.query('INSERT[name=="Part12"]')
    if len(blockrefs):
        entity = blockrefs[0]  # process first entity found
        for attrib in entity.attribs:
            if attrib.dxf.tag == "diameter":  # identify attribute by tag
                attrib.dxf.text = "17mm"  # change attribute content

Get attribute by tag:

.. code-block:: python

    diameter = entity.get_attrib('diameter')
    if diameter is not None:
        diameter.dxf.text = "17mm"


Adding XDATA to Entities
------------------------

Adding XDATA as list of tuples (group code, value) by :meth:`~ezdxf.entities.DXFEntity.set_xdata`, overwrites
data if already present:

.. code-block:: python

    doc.appids.new('YOUR_APPID')  # IMPORTANT: create an APP ID entry

    circle = msp.add_circle((10, 10), 100)
    circle.set_xdata(
        'YOUR_APPID',
        [
            (1000, 'your_web_link.org'),
            (1002, '{'),
            (1000, 'some text'),
            (1002, '{'),
            (1071, 1),
            (1002, '}'),
            (1002, '}')
        ])

For group code meaning see DXF reference section `DXF Group Codes in Numerical Order Reference`_, valid group codes are
in the range 1000 - 1071.

Method :meth:`~ezdxf.entities.DXFEntity.get_xdata` returns the extended data for an entity as
:class:`~ezdxf.lldxf.tags.Tags` object.

.. seealso::

    Tutorial: :ref:`tut_custom_data`

Get Overridden DIMSTYLE Values from DIMENSION
---------------------------------------------

In general the :class:`~ezdxf.entities.Dimension` styling and config attributes are stored in the
:class:`~ezdxf.entities.Dimstyle` entity, but every attribute can be overridden for each DIMENSION
entity individually, get overwritten values by the :class:`~ezdxf.entities.DimstyleOverride` object
as shown in the following example:

.. code-block:: python

    for dimension in msp.query('DIMENSION'):
        dimstyle_override = dimension.override()  # requires v0.12
        dimtol = dimstyle_override['dimtol']
        if dimtol:
            print(f'{str(dimension)} has tolerance values:')
            dimtp = dimstyle_override['dimtp']
            dimtm = dimstyle_override['dimtm']
            print(f'Upper tolerance: {dimtp}')
            print(f'Lower tolerance: {dimtm}')

The :class:`~ezdxf.entities.DimstyleOverride` object returns the value of the underlying DIMSTYLE objects if the
value in DIMENSION was not overwritten, or ``None`` if the value was neither defined in DIMSTYLE nor in DIMENSION.

Override DIMSTYLE Values for DIMENSION
--------------------------------------

Same as above, the :class:`~ezdxf.entities.DimstyleOverride` object supports also overriding DIMSTYLE values.
But just overriding this values have no effect on the graphical representation of the DIMENSION entity, because
CAD applications just show the associated anonymous block which contains the graphical representation on the
DIMENSION entity as simple DXF entities. Call the :class:`~ezdxf.entities.DimstyleOverride.render` method of the
:class:`~ezdxf.entities.DimstyleOverride` object to recreate this graphical representation by `ezdxf`, but `ezdxf`
**does not** support all DIMENSION types and DIMVARS yet, and results **will differ** from AutoCAD
or BricsCAD renderings.

.. code-block:: python

    dimstyle_override = dimension.override()
    dimstyle_override.set_tolerance(0.1)

    # delete associated geometry block
    del doc.blocks[dimension.dxf.geometry]

    # recreate geometry block
    dimstyle_override.render()

How to Change the HATCH Pattern Origin Point
--------------------------------------------

This code sets the origin of the first pattern line to the given `origin` and
the origins of all remaining pattern lines relative to the first pattern line
origin.

.. code-block:: python

    from ezdxf.entities import Hatch, Pattern
    from ezdxf.math import Vec2

    def shift_pattern_origin(hatch: Hatch, offset: Vec2):
        if isinstance(hatch.pattern, Pattern):
            for pattern_line in hatch.pattern.lines:
                pattern_line.base_point += offset

    def reset_pattern_origin_of_first_pattern_line(hatch: Hatch, origin: Vec2):
        if isinstance(hatch.pattern, Pattern) and len(hatch.pattern.lines):
            first_pattern_line = hatch.pattern.lines[0]
            offset = origin - first_pattern_line.base_point
            shift_pattern_origin(hatch, offset)

.. seealso::

    - Discussion `#769 <https://github.com/mozman/ezdxf/discussions/769>`_

How to Get the Length of a Spline or Polyline
---------------------------------------------

There exist no analytical function to calculate the length of a `B-spline`_, you
have to approximate the curve and calculate the length of the polyline.
The construction tool :class:`ezdxf.math.ConstructionPolyline` is may be useful
for that.

.. code-block:: python

    import ezdxf
    from ezdxf.math import ConstructionPolyline

    doc = ezdxf.new()
    msp = doc.modelspace()
    fit_points = [(0, 0, 0), (750, 500, 0), (1750, 500, 0), (2250, 1250, 0)]

    spline = msp.add_spline(fit_points)
    # Adjust the max. sagitta distance to your needs or run the calculation in a loop
    # reducing the distance until the difference to the previous run is smaller
    # than your expected precision:
    polyline = ConstructionPolyline(spline.flattening(distance=0.1))
    print(f"approximated length = {polyline.length:.2f}")

.. _DXF Group Codes in Numerical Order Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3F0380A5-1C15-464D-BC66-2C5F094BCFB9
.. _B-spline: https://en.wikipedia.org/wiki/B-spline
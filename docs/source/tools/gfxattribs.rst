GfxAttribs
==========

.. module:: ezdxf.gfxattribs

.. versionadded:: 0.18

The :mod:`ezdxf.gfxattribs` module provides the :class:`GfxAttribs` class to
create valid attribute dictionaries for the most often used DXF attributes
supported by all graphical DXF entities. The advantage of using this class
is auto-completion support by IDEs and an instant validation of the attribute
values.

.. code-block:: Python

    import ezdxf
    from ezdxf.gfxattribs import GfxAttribs

    doc = ezdxf.new()
    msp = doc.modelspace()

    attribs = GfxAttribs(layer="MyLayer", color=ezdxf.colors.RED)
    line = msp.add_line((0, 0), (1, 0), dxfattribs=attribs)
    circle = msp.add_circle((0, 0), radius=1.0, dxfattribs=attribs)

    # Update DXF attributes of existing entities:
    attribs = GfxAttribs(layer="MyLayer2", color=ezdxf.colors.BLUE)

    # Convert GfxAttribs() to dict(), but this method cannot reset
    # attributes to the default values like setting layer to "0".
    line.update_dxf_attribs(dict(attribs))

    # Using GfxAttribs.asdict(default_values=True), can reset attributes to the
    # default values like setting layer to "0", except for true_color and
    # transparency, which do not have default values, their absence is the
    # default value.
    circle.update_dxf_attribs(attribs.asdict(default_values=True))

    # Remove true_color and transparency by assigning None
    attribs.transparency = None  # reset to transparency by layer!
    attribs.rgb = None


Validation features:

- **layer** - string which can not contain certain characters: ``<>/\":;?*=```
- **color** - :ref:`ACI` value as integer in the range from 0 to 257
- **rgb** - true color value as (red, green, blue) tuple, all channel values as
  integer values in the range from 0 to 255
- **linetype** - string which can not contain certain characters: ``<>/\":;?*=```,
  does not check if the linetype exists
- **lineweight** - integer value in the range from 0 to 211, see :ref:`lineweights`
  for valid values
- **transparency** - float value in the range from 0.0 to 1.0 and -1.0 for transparency by block
- **ltscale** - float value > 0.0


.. autoclass:: GfxAttribs

    .. autoproperty:: layer

    .. autoproperty:: color

    .. autoproperty:: rgb

    .. autoproperty:: linetype

    .. autoproperty:: lineweight

    .. autoproperty:: transparency

    .. autoproperty:: ltscale

    .. automethod:: __str__

    .. automethod:: __repr__

    .. automethod:: __iter__

    .. automethod:: asdict

    .. automethod:: items

    .. automethod:: load_from_header

    .. automethod:: write_to_header

    .. automethod:: from_entity


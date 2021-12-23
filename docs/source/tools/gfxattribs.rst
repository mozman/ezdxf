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
    msp.add_line((0, 0), (1, 0), dxfattribs=dict(attribs))
    msp.add_circle((0, 0), radius=1.0, dxfattribs=dict(attribs))

Validation features:

- **layer** - string which can not contain certain characters: ``<>/\\":;?*=\```
- **color** - :ref:`ACI` value as integer in the range from 0 to 257
- **rgb** - true color value as (red, green blue) tuple, all channel values as
  integer values in the range from 0 to 255
- **linetype** - string which can not contain certain characters: ``<>/\\":;?*=\```,
  does not check if the linetype exists
- **lineweight** - integer value in the range from 0 to 211, see :ref:`lineweights`
  for valid values
- **transparency** - float value in the range from 0.0 to 1.0
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


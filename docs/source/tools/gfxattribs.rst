gfxattribs
==========

.. module:: ezdxf.gfxattribs

.. versionadded:: 0.18

This module provides the :func:`gfxattribs` function to create valid
attribute dictionaries for the most often used DXF attributes supported by all
graphical DXF entities. The advantage of using this function is to get
auto-completion support by IDEs and an instant validation of the attribute
values.

.. code-block:: Python

    import ezdxf
    from ezdxf.gfxattribs import gfxattribs

    doc = ezdxf.new()
    msp = doc.modelspace()

    dxfattribs = gfxattribs(layer="MyLayer", color=ezdxf.colors.RED)
    msp.add_line((0, 0), (1, 0), dxfattribs=dxfattribs)
    msp.add_circle((0, 0), radius=1.0, dxfattribs=dxfattribs)

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


.. autofunction:: gfxattribs

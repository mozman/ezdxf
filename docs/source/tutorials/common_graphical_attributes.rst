.. _tut_common_graphical_attributes:

Tutorial for Common Graphical Attributes
========================================

The graphical attributes :attr:`color`, :attr:`linetype`, :attr:`lineweight`,
:attr:`true_color`, :attr:`transparency`, :attr:`ltscale` and :attr:`invisible`
are available for all graphical DXF entities and are located in the DXF
namespace attribute :attr:`dxf` of the DXF entities.
All these attributes are optional and all except for :attr:`true_color` and
:attr:`transparency` have a default value.

Not all of these attributes are supported by all DXF versions. This table
shows the minimum required DXF version for each attribute:

======= =======================================================
R12     :attr:`color`, :attr:`linetype`
R2000   :attr:`lineweight`, :attr:`ltscale`, :attr:`invisible`
R2004   :attr:`true_color`, :attr:`transparency`
======= =======================================================

Color
-----

Please read the section about the :ref:`aci` to understand the basics.

The usage of the :attr:`~ezdxf.entities.DXFGraphic.dxf.color` attribute is very
straight forward. Setting the value is::

    entity.dxf.color = 1

and getting the value looks like this::

    value = entity.dxf.color

The :attr:`color` attribute has a default value of 256, which means take the
color defined by the layer associated to the entity. The :mod:`ezdxf.colors`
module defines some constants for often used color values::

    entity.dxf.color = ezdxf.colors.RED

The :func:`ezdxf.colors.aci2rgb` function converts the ACI value to the RGB value
of the default modelspace palette.

.. seealso::

    - Basics about :ref:`aci`
    - :mod:`ezdxf.colors` module

True Color
----------

Please read the section about :ref:`true color` to understand the basics.

The easiest way is to use the :attr:`rgb` property to set and get the true color
values as RGB tuples::

    entity.rgb = (255, 128, 16)

The :attr:`rgb` property return ``None`` if the :attr:`true_color` attribute is
not present::

    rgb = entity.rgb
    if rgb is not None:
        r, g, b = rgb

Setting and getting the :attr:`true_color` DXF attribute directly is possible
and the :mod:`ezdxf.colors` module has helper function to convert RGB tuples to
24-bit value and back::

    entity.dxf.true_color = ezdxf.colors.rgb2int(255, 128, 16)

The :attr:`true_color` attribute is optional does not have a default value and
therefore it is not safe to use the attribute directly, check if the attribute
exists beforehand::

    if entity.dxf.hasattr("true_color"):
        r, g, b = ezdxf.colors.int2rgb(entity.dxf.true_color)

or use the :meth:`get` method of the :attr:`dxf` namespace attribute to get a
default value if the attribute does not exist::

    r, g, b = ezdxf.colors.int2rgb(entity.dxf.get("true_color", 0)

.. seealso::

    - Basics about :ref:`true color`
    - :mod:`ezdxf.colors` module

Transparency
------------

Please read the section about :ref:`transparency` to understand the basics.

For the :attr:`transparency` attribute it is not recommended to use the DXF
attribute of the dxf namespace directly, always use the :attr:`~ezdxf.entities.DXFGraphic.transparency`
property of the :class:`~ezdxf.entities.DXFGraphic` base class.
The :attr:`transparency` property is a float value in the range from 0.0 to
1.0 where 0.0 is opaque and 1.0 if fully transparent::

    entity.transparency = 0.5

The default setting for :attr:`transparency` in CAD applications is always
transparency from entity layer, but the :attr:`transparency` property in `ezdxf`
has a default value of 0.0 (opaque), so there are additional entity properties to
check if the transparency value should be taken from the associated entity layer
or from the parent block::

    if entity.is_transparency_by_layer:
        ...
    elif entity.is_transparency_by_block:
        ...
    else:
        ...

.. seealso::

    - Basics about :ref:`transparency`
    - :mod:`ezdxf.colors` module

Linetype
--------

Please read the section about :ref:`linetypes` to understand the basics.

The :attr:`linetype` attribute contains the name of the linetype as string and
can be set by the :attr:`dxf` namespace attribute directly::

    entity.dxf.linetype = "DASHED"  # linetype DASHED must exist!

The :attr:`linetype` attribute is optional and has a default value of "BYLAYER",
so the attribute can always be used without any concerns::

    name = entity.dxf.linetype

.. warning::

    Make sure the linetype you assign to an entity is really defined in the
    linetype table otherwise AutoCAD will not open the DXF file. There are no
    implicit checks for that by `ezdxf` but you can call the
    :meth:`~ezdxf.document.Drawing.audit` method of the DXF document explicitly
    to validate the document before exporting.

`Ezdxf` creates new DXF documents with as little content as possible, this means
only the resources that are absolutely necessary are created.
The :func:`ezdxf.new` function can create some standard linetypes by setting the
argument `setup` to ``True``::

    doc = ezdxf.new("R2010", setup=True)

.. seealso::

    - Basics about :ref:`linetypes`
    - :ref:`tut_linetypes`

Lineweight
----------

Please read the section about :ref:`lineweights` to understand the basics.

The :attr:`lineweight` attribute contains the lineweight as an integer value
and can be set by the :attr:`dxf` namespace attribute directly::

    entity.dxf.lineweight = 25

The :attr:`lineweight` value is the line width in millimeters times 100 e.g.
0.25mm = 25, but only certain values are valid for more information
go to section: :ref:`lineweights`.

Values < 0 have a special meaning and can be imported as constants from
:mod:`ezdxf.lldxf.const`

=== ==================
-1  LINEWEIGHT_BYLAYER
-2  LINEWEIGHT_BYBLOCK
-3  LINEWEIGHT_DEFAULT
=== ==================

The :attr:`lineweight` attribute is optional and has a default value of -1, so
the attribute can always be used without any concerns::

    lineweight = entity.dxf.lineweight

.. important::

    You have to enable the option to show lineweights in your CAD application or
    viewer to see the effect on screen, which is disabled by default, the same
    has to be done in the page setup options for plotting lineweights.

.. code-block:: Python

    # activate on screen lineweight display
    doc.header["$LWDISPLAY"] = 1

.. seealso::

    - Basics about :ref:`lineweights`

Linetype Scale
--------------

The :attr:`ltscale` attribute scales the linetype pattern by a float value and
can be set by the :attr:`dxf` namespace attribute directly::

    entity.dxf.ltscale = 2.0

The :attr:`ltscale` attribute is optional and has a default value of 1.0, so
the attribute can always be used without any concerns::

    scale = entity.dxf.ltscale

.. seealso::

    - Basics about :ref:`linetypes`

Invisible
---------

The :attr:`invisible` attribute an boolean value (0/1) which defines if an
entity is invisible or visible and can be set by the :attr:`dxf` namespace
attribute directly::

    entity.dxf.invisible = 1

The :attr:`invisible` attribute is optional and has a default value of 0, so
the attribute can always be used without any concerns::

    is_invisible = bool(entity.dxf.invisible)


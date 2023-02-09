.. _tut_linetypes:

Tutorial for Creating Linetype Pattern
======================================

Simple line type example:

.. image:: gfx/ltype_simple.jpg

You can define your own linetypes. A linetype definition has a name,
a description and line pattern elements:

.. code-block:: python

    elements = [total_pattern_length, elem1, elem2, ...]

total_pattern_length
    Sum of all linetype elements (absolute values)

elem
    if elem > 0 it is a line, if elem < 0 it is gap, if elem == 0.0 it is a dot

Create a new linetype definition:

.. code-block:: python

    import ezdxf
    from ezdxf.tools.standards import linetypes  # some predefined linetypes

    doc = ezdxf.new()
    msp = doc.modelspace()

    my_line_types = [
        (
            "DOTTED",
            "Dotted .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .",
            [0.2, 0.0, -0.2],
        ),
        (
            "DOTTEDX2",
            "Dotted (2x) .    .    .    .    .    .    .    . ",
            [0.4, 0.0, -0.4],
        ),
        (
            "DOTTED2",
            "Dotted (.5) . . . . . . . . . . . . . . . . . . . ",
            [0.1, 0.0, -0.1],
        ),
    ]
    for name, desc, pattern in my_line_types:
        if name not in doc.linetypes:
            doc.linetypes.add(
                name=name,
                pattern=pattern,
                description=desc,
            )

Setup some predefined linetypes:

.. code-block:: python

    for name, desc, pattern in linetypes():
        if name not in doc.linetypes:
            doc.linetypes.add(
                name=name,
                pattern= pattern,
                description=desc,
            )

Check Available Linetypes
-------------------------

The linetypes object supports some standard Python protocols:

.. code-block:: python


    # iteration
    print("available linetypes:")
    for lt in doc.linetypes:
        print(f"{lt.dxf.name}: {lt.dxf.description}")

    # check for existing linetype
    if "DOTTED" in doc.linetypes:
        pass

    count = len(doc.linetypes) # total count of linetypes

Removing Linetypes
------------------

.. warning::

    Ezdxf does not check if a linetype is still in use and deleting a linetype
    which is still in use generates an **invalid** DXF file. The audit process
    :meth:`~ezdxf.document.Drawing.audit()` of the DXF document removes
    :attr:`linetype` attributes referencing non existing linetypes.

You can delete a linetype:

.. code-block:: python

    doc.layers.remove("DASHED")

This just removes the linetype definition, the :attr:`linetype` attribute of DXF
entities may still refer the removed linetype definition "DASHED" and AutoCAD
will not open DXF files including undefined linetypes.

Tutorial for Creating Complex Linetype Pattern
==============================================

In DXF R13 Autodesk introduced complex linetypes, containing TEXT or SHAPES in
line types.

Complex linetype example with text:

.. image:: gfx/ltype_text.jpg

Complex line type example with shapes:

.. image:: gfx/ltype_shape.jpg


For easy usage the pattern string for complex line types is mostly the same
string as the pattern definition strings in AutoCAD ".lin" files.

Example for complex line type TEXT:

.. code-block:: python

    doc = ezdxf.new("R2018")  # DXF R13 or later is required

    doc.linetypes.add(
        name="GASLEITUNG2",
        # linetype definition string from acad.lin:
        pattern='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
        description= "Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----",
        length=1,  # required for complex line types
    })


The pattern always starts with an "A", the following float values have the same
meaning as for simple linetypes, a value > 0 is a line, a value < 0 is a gap,
and a 0 is a point, the opening square bracket "[" starts the complex part of
the linetype pattern.

The text after the "[" defines the complex linetype:

- A text in quotes (e.g. "GAS") defines a *complex TEXT linetype* and represents
  the pattern text itself.
- A text without quotes is a SHAPE name (in ".lin" files) and defines a
  *complex SHAPE linetype. Ezdxf can not translate this SHAPE name from the
  ".lin" file into the required shape file index, so *YOU* have to translate
  this SHAPE name into the shape file index, e.g. saving the file with AutoCAD
  as DXF and searching for the DXF linetype definition, see example below and
  the DXF Internals: :ref:`ltype_table_internals`.

For *complex TEXT linetypes* the second parameter is the text style,
for *complex SHAPE linetypes* the second parameter is the shape file name,
the shape file has to be in the same directory as the DXF file or in one of the
CAD application support paths.

The meaning of the following comple linetype parameters are shown in the table
below:

======= ===================================================================
 S      scaling factor, always > 0, if S=0 the TEXT or SHAPE is not visible
 R or U rotation relative to the line direction
 X      x-direction offset (along the line)
 Y      y-direction offset (perpendicular to the line)
======= ===================================================================

These parameters are case insensitive and the closing square bracket "]" ends
the complex part of the linetype pattern.

The fine tuning of this parameters is a try an error process, for
*complex TEXT linetypes* the scaling factor (e.g. the STANDARD text style) sets
the text height (e.g. "S=0.1" sets the text height to 0.1 units), by shifting in
y-direction by half of the scaling factor, the text is vertically centered to
the line. For the x-direction it seems to be a good practice to place a gap in
front of the text and after the text, find x shifting value and gap sizes by
try and error. The overall length is at least the sum of all line and gap
definitions (absolute values).

Example for complex line type SHAPE:

.. code-block:: python

    doc.linetypes.add("GRENZE2",
        # linetype definition in acad.lin:
        # A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1
        # replacing BOX by shape index 132 (got index from an AutoCAD file),
        # ezdxf can't get shape index from ltypeshp.shx
        pattern="A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1",
        description="Grenze eckig ----[]-----[]----[]-----[]----[]--",
        length= 1.45,  # required for complex line types
    })

Complex line types with shapes only work if the associated shape file (e. g.
ltypeshp.shx) and the DXF file are in the same directory or the shape file is
placed in one of the CAD application support folders.


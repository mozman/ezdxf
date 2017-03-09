.. _tut_linetypes:

Tutorial for Linetypes
======================

You can define your own line types. A DXF linetype definition consists of name, description and elements::

    elements = [total_pattern_length, elem1, elem2, ...]

total_pattern_length
    Sum of all linetype elements (absolute vaues)

elem
    if eleme > 0 it is a line, if elem < 0 it is gap, if elem == 0.0 it is a dot

Create a new linetype definition::

    import ezdxf
    from ezdxf.tools.standards import linetypes

    dwg = ezdxf.new()
    msp = modelspace()

    my_line_types = [
        ("DOTTED", "Dotted .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .", [0.2, 0.0, -0.2]),
        ("DOTTEDX2", "Dotted (2x) .    .    .    .    .    .    .    . ", [0.4, 0.0, -0.4]),
        ("DOTTED2", "Dotted (.5) . . . . . . . . . . . . . . . . . . . ", [0.1, 0.0, -0.1]),
    ]
    for name, desc, pattern in my_line_types:
        if name not in dwg.linetypes:
            dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})

Setup some predefined linetypes::

    for name, desc, pattern in linetypes():
        if name not in dwg.linetypes:
            dwg.linetypes.new(name=name, dxfattribs={'description': desc, 'pattern': pattern})

Check Available Linetypes
-------------------------

The linetypes object supports some standard Python protocols::

    # iteration
    print('available line types:')
    for linetype in dwg.linetypes:
        print('{}: {}'.format(linetype.dxf.name, linetype.dxf.description))

    # check for existing line type
    if 'DOTTED' in dwg.linetypes:
        pass

    count = len(dwg.linetypes) # total count of linetypes

Removing Linetypes
------------------

.. warning::

    Deleting still used linetypes leads to an invalid DXF files.

You can delete a linetype::

    dwg.layers.remove('DASHED')

This just deletes the linetype definition, all DXF entity with the DXF attribute linetype set to ``DASHED`` still
refers to linetype ``DASHED`` and AutoCAD will not open DXF files with undefined line types.


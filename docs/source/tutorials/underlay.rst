.. _tut_underlay:

Tutorial for Underlay and UnderlayDefinition
============================================

Insert a PDF, DWF, DWFx or DGN file as drawing underlay, the underlay file is NOT embedded into the DXF file::

    import ezdxf


    dwg = ezdxf.new('AC1015')  # underlay requires the DXF R2000 format or newer
    my_underlay_def = dwg.add_underlay_def(filename='my_underlay.pdf')
    # The (PDF)DEFINITION entity is like a block definition, it just defines the underlay

    msp = dwg.modelspace()
    # add first underlay
    msp.add_underlay(my_underlay_def, insert=(2, 1), scale=0.05)
    # The (PDF)UNDERLAY entity is like the INSERT entity, it creates an underlay reference,
    # and there can be multiple references to the same underlay in a drawing.

    msp.add_underlay(my_underlay_def, insert=(4, 5), scale=.5, rotation=30)

    # get existing underlay definitions, Important: UNDERLAYDEFs resides in the objects section
    pdf_defs = dwg.objects.query('PDFDEFINITION')  # get all pdf underlay defs in drawing

    dwg.saveas("dxf_with_underlay.dxf")


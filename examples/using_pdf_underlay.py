import ezdxf

dwg = ezdxf.new('AC1015')  # underlay requires the DXF R2000 format or newer
pdf_underlay_def = dwg.add_underlay_def(filename='underlay.pdf', name='1')  # name = page to display
dwf_underlay_def = dwg.add_underlay_def(filename='underlay.dwf', name="Underlay_R2013-Model")  # don't know how to get this name
dgn_underlay_def = dwg.add_underlay_def(filename='underlay.dgn', name='default')  # name = 'default' just works

# The (PDF)DEFINITION entity is like a block definition, it just defines the underlay
dwg.header['$MEASUREMENT'] = 1
msp = dwg.modelspace()
# add first underlay
msp.add_underlay(pdf_underlay_def, insert=(0, 0, 0), scale=1.)
# The (PDF)UNDERLAY entity is like the INSERT entity, it creates an underlay reference,
# and there can be multiple references to the same underlay in a drawing.
msp.add_underlay(pdf_underlay_def, insert=(10, 0, 0), scale=.5, rotation=30)

# use dgn format
msp.add_underlay(dgn_underlay_def, insert=(0, 30, 0), scale=1.)

# use dwf format
msp.add_underlay(dwf_underlay_def, insert=(0, 15, 0), scale=1.)


# get existing underlay definitions, Important: UNDERLAYDEFs resides in the objects section
pdf_defs = dwg.objects.query('PDFDEFINITION')  # get all pdf underlay defs in drawing

dwg.saveas("dxf_with_underlay.dxf")


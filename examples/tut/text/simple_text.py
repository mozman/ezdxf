import ezdxf

dwg = ezdxf.new('AC1009')  # TEXT is a basic entity and exists in every DXF standard

msp = dwg.modelspace()

# use set_pos() for proper TEXT alignment - the relations between halign, valign, insert and align_point are tricky.
msp.add_text("A Simple Text").set_pos((2, 3), align='MIDDLE_RIGHT')

# using text styles
dwg.styles.new('custom', dxfattribs={'font': 'arial.ttf', 'width': 0.8})  # Arial, default width factor of 0.8
msp.add_text("Text Style Example", dxfattribs={'style': 'custom', 'height': 0.35}).set_pot((2, 6), align='LEFT')

dwg.saveas("simple_text.dxf")

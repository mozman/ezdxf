import ezdxf

dwg = ezdxf.new('AC1009')  # TEXT is a basic entity and exists in every DXF standard

msp = dwg.modelspace()
# use set_pos() for proper TEXT alignment - the relations between halign, valign, insert and align_point are tricky.
msp.add_text("simple text").set_pos((2, 3), align='MIDDLE_RIGHT')

dwg.saveas("simple_text.dxf")

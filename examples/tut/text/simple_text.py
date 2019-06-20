import ezdxf

doc = ezdxf.new('R12', setup=True)  # TEXT is a basic entity and exists in every DXF standard
# setup=True for adding standard line types and text styles
msp = doc.modelspace()

# use set_pos() for proper TEXT alignment - the relations between halign, valign, insert and align_point are tricky.
msp.add_text("A Simple Text").set_pos((2, 3), align='MIDDLE_RIGHT')

# using text styles
msp.add_text("Text Style Example: Liberation Serif", dxfattribs={'style': 'LiberationSerif', 'height': 0.35}).set_pos((2, 6), align='LEFT')

doc.saveas("simple_text.dxf")

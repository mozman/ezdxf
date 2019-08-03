import ezdxf

# TEXT is a basic entity and is supported by every DXF version.
# Argument setup=True for adding standard linetypes and text styles.
doc = ezdxf.new('R12', setup=True)
msp = doc.modelspace()

# use set_pos() for proper TEXT alignment:
# The relations between DXF attributes 'halign', 'valign',
# 'insert' and 'align_point' are tricky.
msp.add_text("A Simple Text").set_pos((2, 3), align='MIDDLE_RIGHT')

# Using a text style
msp.add_text("Text Style Example: Liberation Serif",
             dxfattribs={
                 'style': 'LiberationSerif',
                 'height': 0.35}
             ).set_pos((2, 6), align='LEFT')

doc.saveas("simple_text.dxf")

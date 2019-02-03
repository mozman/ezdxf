# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

# include-start
import ezdxf
from ezdxf.math import UCS, Vector

dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

# thickness for text works only with shx fonts not with true type fonts
dwg.styles.new('TXT', dxfattribs={'font': 'romans.shx'})

ucs = UCS(origin=(0, 2, 2), ux=(1, 0, 0), uz=(0, 1, 1))
# calculation of text direction as angle in OCS:
# convert text rotation in degree into a vector in UCS
text_direction = Vector.from_deg_angle(-45)
# transform vector into OCS and get angle of vector in xy-plane
rotation = ucs.to_ocs(text_direction).angle_deg

text = msp.add_text(
    text="TEXT",
    dxfattribs={
        # text rotation angle in degrees in OCS
        'rotation': rotation,
        'extrusion': ucs.uz,
        'thickness': .333,
        'color': 2,
        'style': 'TXT',
    })
# set text position in OCS
text.set_pos(ucs.to_ocs((0, 0, 0)), align='MIDDLE_CENTER')

# include-end

ucs.render_axis(msp)
dwg.saveas('ocs_text.dxf')

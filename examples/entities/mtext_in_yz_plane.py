# Created: 18.02.2017
# Copyright (c) 2017-2019 Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new('R2000')
modelspace = doc.modelspace()
modelspace.add_mtext("This is a text in the YZ-plane",
                     dxfattribs={
                         'width': 12,  # reference rectangle width
                         'text_direction': (0, 1, 0),  # write in y direction
                         'extrusion': (1, 0, 0)  # normal vector of the text plane
                     })

doc.saveas('mtext_in_yz_plane.dxf')


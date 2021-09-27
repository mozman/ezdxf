# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new("R2007", setup=True)
msp = doc.modelspace()

# add default leader style
msp.add_leader(vertices=[(0, 0), (2, 2), (4, 2)])

# add leader with style override
msp.add_leader(
    vertices=[(10, 0), (12, 2), (14, 2)], override={"dimldrblk": "CLOSEDBLANK"}
)

# I don't know how to to use text, tolerance or block reference annotations, but
# you can draw the text as unrelated entity.

msp.add_text(
    "Text",
    dxfattribs={
        "style": "OpenSans",
        "height": 0.25,
    },
).set_pos((4, 5), align="MIDDLE_LEFT")
msp.add_leader(vertices=[(0, 3), (2, 5), (4, 5)])

# For more information look at the Autodesk documentation.
# or https://atlight.github.io/formats/dxf-leader.html


filename = "leader.dxf"
doc.saveas(filename)
print("drawing '%s' created.\n" % filename)

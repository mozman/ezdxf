# Copyright (c) 2016-2021 Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new("R12", setup=True)
modelspace = doc.modelspace()
modelspace.add_circle(
    center=(0, 0),
    radius=1.5,
    dxfattribs={
        "layer": "test",
        "linetype": "DASHED",
    },
)

filename = "circle.dxf"
doc.saveas(filename)
print("drawing '%s' created.\n" % filename)

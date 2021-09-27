# Copyright (c) 2016-2021 Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new("R2000")
modelspace = doc.modelspace()
modelspace.add_ellipse(
    center=(0, 0),
    major_axis=(3, 1),
    ratio=0.65,
    dxfattribs={
        "layer": "test",
        "linetype": "DASHED",
    },
)

filename = "ellipse.dxf"
doc.saveas(filename)
print("drawing '%s' created.\n" % filename)

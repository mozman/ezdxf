# Copyright (c) 2017-2021 Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new("R2018", setup=True)
modelspace = doc.modelspace()
modelspace.add_circle(
    center=(0, 0),
    radius=1.5,
    dxfattribs={
        "layer": "test",
        "linetype": "DASHED",
    },
)

filename = "circle_R2018.dxf"
doc.saveas(filename)
print(f"DXF file '{filename}' created.")

# Copyright (c) 2018-2023 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.fonts import shapefile

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


# ------------------------------------------------------------------------------
# This example shows how to create complex linetypes.
#
# docs: https://ezdxf.mozman.at/docs/concepts/linetypes.html
# ------------------------------------------------------------------------------

doc = ezdxf.new("R2018")  # DXF R13 or later is required

# This linetype contains the text "GAS" with text-style "STANDARD"
doc.linetypes.add(
    "GASLEITUNG2",
    # linetype definition in acadlt.lin:
    pattern='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
    description="Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--",
    length=1,  # required for complex linetypes
)

# This linetype contains a box shape from the ltypeshp.shx file.
#
# Shapes in linetypes require the referenced shape-file (ltypeshp.shx in this
# case) to be located in the search path of the CAD application or in the same
# folder as the DXF file.
doc.linetypes.add(
    "GRENZE2",
    # Get the linetype definition from acadlt.lin:
    # "A,.25,-.1,[BOX,ltypeshp.shx,x=-.1,s=.1],-.1,1" and replace "BOX" by
    # shape-number 132.
    # Find the shape-number by function find_shape_number(), the SHX file "ltypeshp.shx"
    # will be searched in the current directory and the directories stored in
    # `ezdxf.options.support_dirs`.
    pattern="A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1",
    description="Grenze eckig -[]-----[]-----[]-----[]-----[]----",
    length=1.45,  # required for complex line types
)
print(shapefile.find_shape_number("ltypeshp.shx", b"BOX"))

msp = doc.modelspace()
msp.add_line((0, 0), (100, 0), dxfattribs={"linetype": "GASLEITUNG2"})
msp.add_line((0, 50), (100, 50), dxfattribs={"linetype": "GRENZE2"})

zoom.extents(msp, 1.1)
doc.saveas(CWD / "complex_linetype_example.dxf")

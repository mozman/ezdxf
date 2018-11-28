# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
import os
import ezdxf

DIMPATH = r"D:\Source\dxftest\dimlines"

dwg = ezdxf.readfile(os.path.join(DIMPATH, "linear_R2000.dxf"))

for dimstyle in dwg.dimstyles:
    print("Dimstyle: {}".format(dimstyle.dxf.name))
    print("flags: {:x}".format(dimstyle.dxf.flags))
    dimstyle.print_attribs()
    print("-"*20)

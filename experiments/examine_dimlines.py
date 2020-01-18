# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
import os
import ezdxf

DIMPATH = r"C:\Users\manfred\Desktop\outbox"

doc = ezdxf.readfile(os.path.join(DIMPATH, "brics_R2000.dxf"))

for dimstyle in doc.dimstyles:
    print("Dimstyle: {}".format(dimstyle.dxf.name))
    print("flags: {:x}".format(dimstyle.dxf.flags))
    dimstyle.print_dim_attribs()
    print("-"*20)

# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import ezdxf

doc = ezdxf.new()
msp = doc.modelspace()
with open("msp_factory_method_index.rst", "wt") as fp:
    for name in dir(msp.__class__):
        if name.startswith("add_"):
            fp.write(f"- :meth:`~ezdxf.layouts.BaseLayout.{name}`\n")

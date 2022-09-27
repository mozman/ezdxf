# Copyright (c) 2018-2022 Manfred Moitzi
# License: MIT License
import pathlib
from time import perf_counter
import ezdxf
from ezdxf.addons import SierpinskyPyramid

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example creates some Sierpinski pyramids.
#
# docs: https://ezdxf.mozman.at/docs/addons/forms.html
# ------------------------------------------------------------------------------


def write(filename, pyramids, merge=False):
    doc = ezdxf.new("R2000")
    doc.set_modelspace_vport(3)
    pyramids.render(doc.modelspace(), merge=merge)
    doc.saveas(filename)


def main(filename, level, sides=3, merge=False):
    t0 = perf_counter()
    pyramids = SierpinskyPyramid(level=level, sides=sides)
    t1 = perf_counter()
    print(f"Build sierpinski pyramid {sides} in {t1 - t0:.5f}s.")
    try:
        write(filename, pyramids, merge=merge)
    except IOError as e:
        print(f'ERROR: can not write "{e.filename}": {e.strerror}')
    else:
        print(f'Saved as "{filename}"')


if __name__ == "__main__":
    main(CWD / "sierpinski_pyramid_3.dxf", level=4, sides=3)
    main(CWD / "sierpinski_pyramid_4.dxf", level=4, sides=4, merge=True)

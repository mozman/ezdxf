# Copyright (c) 2018-2022 Manfred Moitzi
# License: MIT License
import pathlib
from time import perf_counter
import ezdxf
from ezdxf.addons import MengerSponge

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example creates come Menger-Sponges.
#
# docs: https://ezdxf.mozman.at/docs/addons/forms.html
# ------------------------------------------------------------------------------


def write(filename, sponge, merge=False):
    doc = ezdxf.new("R2000")
    doc.set_modelspace_vport(3)
    sponge.render(doc.modelspace(), merge=merge)
    doc.saveas(filename)


def main(filename, level=3, kind=0, merge=False):
    t0 = perf_counter()
    sponge = MengerSponge(level=level, kind=kind)
    t1 = perf_counter()
    print(f"Build menger sponge <{kind}> in {t1 - t0:.5f}s.")

    try:
        write(filename, sponge, merge)
    except IOError as e:
        print(f'ERROR: can not write "{e.filename}": {e.strerror}')
    else:
        print(f'saved as "{filename}".')


if __name__ == "__main__":
    main(CWD / "menger_sponge_0.dxf", level=3, kind=0)
    main(CWD / "menger_sponge_1.dxf", level=3, kind=1)
    main(CWD / "menger_sponge_2.dxf", level=3, kind=2)
    main(CWD / "jerusalem_cube.dxf", level=2, kind=3, merge=True)

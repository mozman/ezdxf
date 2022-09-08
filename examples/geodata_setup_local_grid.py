#  Copyright (c) 2020-2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf import units

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# create a GEODATA object for a local grid
#
# docs: https://ezdxf.mozman.at/docs/dxfobjects/geodata.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new("R2010", units=units.M)
    msp = doc.modelspace()
    geodata = msp.new_geodata()
    geodata.setup_local_grid(
        design_point=(0, 0), reference_point=(1718030, 5921664)
    )
    msp.add_line((0, 0), (100, 0))
    doc.set_modelspace_vport(50, center=(50, 0))
    doc.saveas(CWD / "geodata_local_grid.dxf")


if __name__ == "__main__":
    main()

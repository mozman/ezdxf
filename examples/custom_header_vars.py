# Copyright (c) 2014-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# create custom HEADER variables
#
# for more information about custom HEADER variables see:
# https://ezdxf.mozman.at/docs/tutorials/custom_data.html#custom-document-properties
# ------------------------------------------------------------------------------


def main():
    # this feature requires DXF R2000 or later
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    # create some content
    points = [(0, 0), (3, 0), (6, 3), (6, 6)]
    msp.add_polyline2d(points)

    # create custom HEADER variables
    doc.header.custom_vars.append("Name", "Manfred Moitzi")
    doc.header.custom_vars.append("Adresse", "8020 Graz")
    doc.saveas(CWD / "custom_header_vars.dxf")


if __name__ == "__main__":
    main()

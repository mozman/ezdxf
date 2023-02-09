# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

import pathlib
import ezdxf
from ezdxf.render import forms
from ezdxf.acis import api as acis

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create a simple ACIS cube for all supported DXf versions.
#
# docs: https://ezdxf.mozman.at/docs/tools/acis.html
# ------------------------------------------------------------------------------


def run(version: str):
    doc = ezdxf.new(version, setup=True)
    msp = doc.modelspace()

    # create the DXF 3DSOLID entity
    solid3d = msp.add_3dsolid()
    # create the ACIS body entity from the cube-mesh
    cube = forms.cube()
    body = acis.body_from_mesh(cube)
    acis.export_dxf(solid3d, [body])

    doc.set_modelspace_vport(5)
    doc.saveas(CWD / f"acis_cube_{version}.dxf")


def main():
    for version in ["R2000", "R2004", "R2007", "R2010", "R2013", "R2018"]:
        run(version)


if __name__ == '__main__':
    main()

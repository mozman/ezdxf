# Copyright (c) 2021-2022 Manfred Moitzi
# License: MIT License
import pathlib

import ezdxf
from ezdxf.math import Matrix44, TransformError
from ezdxf.layouts import BaseLayout


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to transform all entities of a layout by the
# general transformation interface.
# docs: https://ezdxf.mozman.at/docs/dxfentities/dxfgfx.html#ezdxf.entities.DXFGraphic.transform
# ------------------------------------------------------------------------------

EXAMPLE = (
    ezdxf.options.test_files_path / "CADKitSamples" / "AEC Plan Elev Sample.dxf"
)
INCH_TO_MM = 25.4


def transform_layout(layout: BaseLayout, m: Matrix44) -> None:
    for entity in layout:
        try:
            entity.transform(m)
        except (NotImplementedError, TransformError):
            pass


doc = ezdxf.readfile(EXAMPLE)
transform_layout(doc.modelspace(), Matrix44.scale(INCH_TO_MM))
doc.saveas(CWD / "scaled.dxf")

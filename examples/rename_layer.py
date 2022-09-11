# Copyright (c) 2018-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.document import Drawing

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to rename layers.
#
# The DXF format is not consistent in storing layer references, the
# layers are mostly referenced by their case-insensitive name, and in
# some entities introduced later, layers are referenced by their handle.
# There is also not a complete overview of where layer references are
# stored, which means that it is not 100% safe to rename layers via
# ezdxf, so in some rare cases renaming layers can corrupt the DXF
# file!
#
# docs: https://ezdxf.mozman.at/docs/tables/layer_table_entry.html#layer
# ------------------------------------------------------------------------------

OLD_LAYER_NAME = "LAYER_1"
NEW_LAYER_NAME = "MOZMAN"


def create_doc() -> Drawing:
    doc = ezdxf.new()
    layer = doc.layers.add(OLD_LAYER_NAME)
    msp = doc.modelspace()
    attribs = dict(layer=layer.dxf.name)
    msp.add_line((0, 0), (1, 0), dxfattribs=attribs)
    msp.add_circle((0, 0), radius=1, dxfattribs=attribs)
    msp.add_point((2, 0), dxfattribs=attribs)
    return doc


def main():
    doc = create_doc()
    msp = doc.modelspace()
    layer = doc.layers.get(OLD_LAYER_NAME)
    layer.rename(NEW_LAYER_NAME)

    entities = msp.query(f'*[layer=="{NEW_LAYER_NAME}"]')
    assert len(entities) == 3
    doc.saveas(CWD / "renamed_layer.dxf")


if __name__ == "__main__":
    main()

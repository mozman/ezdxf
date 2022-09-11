# Copyright (c) 2015-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to manage DXF entities as a GROUP.
# ------------------------------------------------------------------------------


def create_group():
    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    # Create a new unnamed GROUP, in reality they have a name like '*Annnn' and
    # group names have to be unique.
    group = doc.groups.new()

    # The group management is implemented as context manager, returning a
    # standard Python list
    with group.edit_data() as g:
        # The group itself is not an entity-space, DXF entities has to be
        # located in modelspace, paperspace or in a block.
        g.append(msp.add_line((0, 0), (3, 0)))
        g.append(msp.add_circle((0, 0), radius=2))
    doc.saveas(CWD / "group.dxf")


def read_group():
    doc = ezdxf.readfile(CWD / "group.dxf")
    for name, group in doc.groups:
        print(f"GROUP: {name}\n")
        for entity in group:
            print(f"  ENTITY: {entity.dxftype()}")


if __name__ == "__main__":
    create_group()
    read_group()

# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf

from ezdxf.entities import DXFTagStorage
from ezdxf.entities.acad_table import read_acad_table_content

CWD = Path(__file__).parent.parent.parent / "examples_dxf"


def main() -> None:
    doc = ezdxf.readfile(CWD / "acad_table_with_blk_ref.dxf")
    msp = doc.modelspace()
    table: DXFTagStorage = msp.query("ACAD_TABLE").first
    values = read_acad_table_content(table)
    print("Table Values:")
    print(values)


if __name__ == "__main__":
    main()

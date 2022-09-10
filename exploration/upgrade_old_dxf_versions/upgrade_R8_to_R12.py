#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf

DIR = Path(ezdxf.EZDXF_TEST_FILES) / "R8_test_files"


def upgrade_dxf_file(name):
    print(f"upgrade {name} to R12")
    dwg = ezdxf.readfile(DIR / name)
    dwg.saveas(DIR / "as_R12" / name)


def main():
    for dxf_file in DIR.glob("*.dxf"):
        name = dxf_file.name
        upgrade_dxf_file(name)


if __name__ == "__main__":
    main()

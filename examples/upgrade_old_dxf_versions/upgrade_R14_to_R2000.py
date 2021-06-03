from pathlib import Path
import ezdxf

DIR = Path(ezdxf.EZDXF_TEST_FILES) / "R14_test_files"


def upgrade_dxf_file(name):
    print(f"upgrade {name} to R2000")
    dwg = ezdxf.readfile(DIR / name)
    dwg.saveas(DIR / "as_R2000" / name)


def main():
    for dxf_file in DIR.glob("*.dxf"):
        name = dxf_file.name
        upgrade_dxf_file(name)


if __name__ == "__main__":
    main()
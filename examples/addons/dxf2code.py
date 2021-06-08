from pathlib import Path
import ezdxf
from ezdxf.addons.dxf2code import entities_to_code

FILENAME = "A_000217"
CADKIT = Path(ezdxf.EZDXF_TEST_FILES) / "CADKitSamples"
OUTBOX = Path("~/Desktop/Outbox").expanduser()

DXF_FILE = CADKIT / f"{FILENAME}.dxf"
SOURCE_CODE_FILE = OUTBOX / f"{FILENAME}.py"

doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

source = entities_to_code(msp, layout="msp")

print("writing " + str(SOURCE_CODE_FILE))
with open(SOURCE_CODE_FILE, mode="wt") as f:
    f.write("import ezdxf\n")
    f.write(source.import_str())
    f.write("\n\n")

    f.write("doc = ezdxf.new()\n")
    f.write("msp = ezdxf.modelspace()\n\n")
    f.write(source.code_str())
    f.write("\n")

print("done.")

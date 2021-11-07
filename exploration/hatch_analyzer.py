from pathlib import Path
import ezdxf
from ezdxf.entities import Hatch

from ezdxf.tools.analyze import HatchAnalyzer

DIR = Path("~/Desktop/Outbox").expanduser()
FILE = r"C:\Users\manfred\Desktop\Now\ezdxf\573\textbox.dxf"

doc = ezdxf.readfile(FILE)
hatch = doc.entitydb.get("A2")
assert isinstance(hatch, Hatch)

handle = hatch.dxf.handle
hatch_analyzer = HatchAnalyzer(marker_size=10)
hatch_analyzer.print_report(hatch)
hatch_analyzer.add_hatch(hatch)
hatch_analyzer.add_boundary_markers(hatch)
hatch_analyzer.export(str(DIR / f"hatch_{handle}.dxf"))

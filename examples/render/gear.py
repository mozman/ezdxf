from pathlib import Path
import ezdxf
from ezdxf.render.forms import gear

DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()
msp.add_lwpolyline(
    gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10),
    close=True,
)
doc.saveas(DIR / "gear.dxf")

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf

DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

line = msp.add_line((0, 0), (1, 0))
line2 = msp.add_line((0, 2), (1, 2))

if line.has_extension_dict:
    xdict = line.get_extension_dict()
else:
    xdict = line.new_extension_dict()

xrecord = xdict.add_xrecord("DATA1")
xrecord.reset([
    (1, "text1"),  # string
    (40, 3.141592),  # float
    (90, 256),  # 32-bit int
    (10, (1, 2, 0)),  # points and vectors
    (330, line2.dxf.handle)  # handles
])

print(xrecord.tags)


doc.saveas(DIR / "xrecord.dxf")

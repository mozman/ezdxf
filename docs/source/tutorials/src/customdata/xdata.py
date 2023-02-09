#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

# register your appid
APPID = "YOUR_UNIQUE_ID"
doc.appids.add(APPID)

# create a DXF entity
line = msp.add_line((0, 0), (1, 0))

# setting the data
line.set_xdata(APPID, [
    # basic types
    (1000, "custom text"),
    (1040, 3.141592),
    (1070, 4711),  # 16bit
    (1071, 1_048_576),  # 32bit
    # points and vectors
    (1010, (10, 20, 30)),
    (1011, (11, 21, 31)),
    (1012, (12, 22, 32)),
    (1013, (13, 23, 33)),
    # scaled distances and factors
    (1041, 10),
    (1042, 10),
])

# getting the data
if line.has_xdata(APPID):
    tags = line.get_xdata(APPID)
    print(f"{str(line)} has {len(tags)} tags of XDATA for AppID {APPID!r}")
    for tag in tags:
        print(tag)

doc.saveas(DIR / "xdata.dxf")

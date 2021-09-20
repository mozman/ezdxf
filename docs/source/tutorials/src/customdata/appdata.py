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
line.set_app_data(APPID, [(300, "custom text"), (370, 4711), (460, 3.141592)])

# getting the data
if line.has_app_data(APPID):
    tags = line.get_app_data(APPID)
    print(f"{str(line)} has {len(tags)} tags of AppData for AppID {APPID!r}")
    for tag in tags:
        print(tag)

doc.saveas(DIR / "appdata.dxf")

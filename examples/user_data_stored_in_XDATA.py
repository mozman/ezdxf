#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License

import pathlib
import ezdxf
from ezdxf.math import Vec3
from ezdxf.render.forms import gear
from ezdxf import zoom
from ezdxf.entities.xdata import XDataUserDict, XDataUserList

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to store user data in the XDATA section of DXF entities.
# docs: https://ezdxf.mozman.at/docs/user_xdata.html#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/custom_data.html
# ------------------------------------------------------------------------------

doc = ezdxf.new()
msp = doc.modelspace()
gear = msp.add_lwpolyline(
    gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10),
    close=True,
)
handle = gear.dxf.handle

# default dict name = "DefaultDict"
# default appid = "EZDXF"
# If using an own AppID, don't forget to create the requited AppID table entry
# e.g. doc.appids.new("MyAppID"), otherwise AutoCAD will not open the DXF file.

# Supported data: str, int, float and Vec3

with XDataUserDict.entity(gear) as user_dict:
    # has a dict-like interface
    user_dict["CreatedBy"] = "mozman"
    user_dict["Float"] = 3.1415
    user_dict["Int"] = 4711
    user_dict["Point"] = Vec3(1, 2, 3)

# The XDATA structure looks like this:
#   0
# LWPOLYLINE
# ...
# 1001
# EZDXF
# 1000
# DefaultDict
# 1002
# {
# 1000
# CreatedBy
# 1000
# mozman
# 1000
# Float
# 1040
# 3.1415
# 1000
# Int
# 1071
# 4711
# 1000
# Point
# 1010
# 1.0
# 1020
# 2.0
# 1030
# 3.0
# 1002
# }

# default list name = "DefaultList"
with XDataUserList.entity(gear, name="AppendedPoints") as user_list:
    # has a list-like interface
    user_list.append(Vec3(1, 0, 0))
    user_list.append(Vec3(0, 1, 0))
    user_list.append(Vec3(0, 0, 1))

# The XDATA structure looks like this:
#   0
# LWPOLYLINE
# ...
# 1001
# EZDXF
# 1000
# DefaultDict
# ...
# 1000
# AppendedPoints
# 1002
# {
# 1010
# 1.0
# 1020
# 0.0
# 1030
# 0.0
# 1010
# 0.0
# 1020
# 1.0
# 1030
# 0.0
# 1010
# 0.0
# 1020
# 0.0
# 1030
# 1.0
# 1002
# }

# XDATA will be preserved by AutoCAD, BricsCAD and of course ezdxf.

zoom.objects(msp, [gear])
doc.saveas(CWD / "gear_with_xdata.dxf")

# Retrieve data:
doc2 = ezdxf.readfile(CWD / "gear_with_xdata.dxf")
loaded_gear = doc2.entitydb.get(handle)


with XDataUserDict.entity(loaded_gear) as user_dict:
    print(user_dict)
    # acts like any other dict()
    storage = dict(user_dict)

print(f"Copy of XDataUserDict: {storage}")


with XDataUserList.entity(loaded_gear, name="AppendedPoints") as user_list:
    print(user_list)
    storage = list(user_list)

print(f"Copy of XDataUserList: {storage}")

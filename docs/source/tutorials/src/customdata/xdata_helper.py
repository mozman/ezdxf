#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.math import Vec3
from ezdxf.entities.xdata import XDataUserDict, XDataUserList

DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()
line = msp.add_line((0, 0), (1, 0))

with XDataUserDict.entity(line) as user_dict:
    user_dict["CreatedBy"] = "mozman"
    user_dict["Float"] = 3.1415
    user_dict["Int"] = 4711
    user_dict["Point"] = Vec3(1, 2, 3)


with XDataUserDict.entity(line) as user_dict:
    print(user_dict)
    # acts like any other dict()
    storage = dict(user_dict)

print(f"Copy of XDataUserDict: {storage}")

with XDataUserList.entity(line, name="AppendedPoints") as user_list:
    user_list.append(Vec3(1, 0, 0))
    user_list.append(Vec3(0, 1, 0))
    user_list.append(Vec3(0, 0, 1))


with XDataUserList.entity(line, name="AppendedPoints") as user_list:
    print(user_list)
    storage = list(user_list)

print(f"Copy of XDataUserList: {storage}")
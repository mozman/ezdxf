#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.math import Vec3
from ezdxf.render.forms import gear
from ezdxf import zoom
from ezdxf.urecord import UserRecord, BinaryRecord

DIR = Path("~/Desktop/Outbox").expanduser()

# XRECORD need DXF version R2000+ and does not work with DXF R12 or older.

doc = ezdxf.new()
msp = doc.modelspace()
gear = msp.add_lwpolyline(
    gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10),
    close=True,
)
handle = gear.dxf.handle

# 1. Store entity specific data in the associated extension dict
with UserRecord(doc=doc) as user_record:
    # Store user record in the extension dict
    # The extension dict is the owner the XRECORD!
    xdict = gear.new_extension_dict()
    xdict.link_dxf_object("MyData", user_record.xrecord)
    # Supported types: string, int, float, Vec3, (nested) list, (nested) dict
    user_record.data = [
        "MyString",
        4711,
        3.1415,
        Vec3(1, 2, 3),
        {
            "MyIntList": [1, 2, 3],
            "MyFloatList": [4.5, 5.6, 7.8],
        },
    ]
    # Important!
    # Geometric properties like length values, scale factors or vertices
    # stored in XRECORD entities will NOT be transformed with the owner entity!


zoom.objects(msp, [gear])
doc.saveas(DIR / "gear_with_xdict.dxf")

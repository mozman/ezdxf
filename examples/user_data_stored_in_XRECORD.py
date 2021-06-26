#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Optional
from pathlib import Path
from pprint import pprint
import ezdxf
from ezdxf.math import Vec3
from ezdxf.render.forms import gear
from ezdxf import zoom
from ezdxf.urecord import UserRecord, BinaryRecord
from ezdxf.entities import XRecord, DXFEntity
import zlib

DIR = Path("~/Desktop/Outbox").expanduser()

# XRECORD need DXF version R2000+ and does not work with DXF R12 or older.

doc = ezdxf.new()
msp = doc.modelspace()
gear_ = msp.add_lwpolyline(
    gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10),
    close=True,
)
handle = gear_.dxf.handle

# ------------------------------------------------------------------------------
# Example 1: Store entity specific data in the associated extension dict

with UserRecord(doc=doc) as user_record:
    # A new XRECORD object was created in the DXF document `doc` and stored
    # in the attribute `user_record.xrecord`.
    # Create a new extension dict for the LWPOLYLINE entity.
    xdict = gear_.new_extension_dict()

    # Store the `user_record` in the extension dict by key "MyData".
    # The extension dict is the owner the XRECORD!
    xdict.link_dxf_object("MyData", user_record.xrecord)

    # Supported types: string, int, float, Vec3, (nested) list, (nested) dict
    # The str type has a DXF format limit of 2049 characters and cannot contain
    # the line endings '\n' or '\r'.
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

# ------------------------------------------------------------------------------
# Example 2: Store arbitrary data in DICTIONARY objects.

# Get the existing DICTIONARY object or create a new DICTIONARY object:
my_dict = doc.objects.rootdict.get_required_dict("MyDict")

# Create a new XRECORD object, the DICTIONARY object is the owner of this
# new XRECORD:
xrecord = my_dict.add_xrecord("MyData")

# This examples creates the user record without the context manager.
user_record = UserRecord(xrecord)

# Store user data:
user_record.data = [
    "Just another user record",
    4711,
    3.1415,
]
# Store user data in associated XRECORD:
user_record.commit()

# ------------------------------------------------------------------------------
# Example 3: Store arbitrary binary data

my_dict = doc.rootdict.get_required_dict("MyDict")
xrecord = my_dict.add_xrecord("MyBinaryData")
with BinaryRecord(xrecord) as binary_record:
    # The content is stored as hex strings (e.g. ABBAFEFE...) in one or more
    # group code 310 tags.
    # A preceding group code 160 tag stores the data size in bytes.
    data = b"Store any binary data, even line breaks\r\n" * 20
    # compress data if required
    binary_record.data = zlib.compress(data, level=9)

zoom.objects(msp, [gear_])
doc.saveas(DIR / "gear_with_user_data.dxf")

# ------------------------------------------------------------------------------
# Retrieving data from reloaded DXF file
# ------------------------------------------------------------------------------

doc = ezdxf.readfile(DIR / "gear_with_user_data.dxf")
gear_ = doc.entitydb.get(handle)
entity: Optional[DXFEntity]

# ------------------------------------------------------------------------------
# Example 1: Get entity specific data from the associated extension dict

print("\nContent of example 1:")
if gear_.has_extension_dict:
    xdict = gear_.get_extension_dict()
    entity = xdict.get("MyData")
    if entity is not None:
        assert isinstance(entity, XRecord)
        user_record = UserRecord(entity)
        pprint(user_record.data)

# ------------------------------------------------------------------------------
# Example 2: Get user data from DICTIONARY object

print("\nContent of example 2:")
my_dict = doc.rootdict.get_required_dict("MyDict")
entity = my_dict["MyData"]
if entity is not None:
    assert isinstance(entity, XRecord)
    user_record = UserRecord(entity)
    pprint(user_record.data)

# ------------------------------------------------------------------------------
# Example 3: Get binary data from DICTIONARY object

print("\nContent of example 3:")
entity = my_dict["MyBinaryData"]
if entity is not None:
    assert isinstance(entity, XRecord)
    binary_record = BinaryRecord(entity)
    print("\ncompressed data:")
    pprint(binary_record.data)

    print("\nuncompressed data:")
    pprint(zlib.decompress(binary_record.data))

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
from ezdxf import zoom
from pprint import pprint
import ezdxf
from ezdxf.math import Vec3
from ezdxf.urecord import UserRecord, BinaryRecord
from ezdxf.entities import XRecord
import zlib

DIR = Path("~/Desktop/Outbox").expanduser()

# XRECORD need DXF version R2000+ and does not work with DXF R12 or older.

doc = ezdxf.new()
msp = doc.modelspace()

# ------------------------------------------------------------------------------
# Example 1: Store entity specific data in the associated extension dict

line = msp.add_line((0, 0), (1, 0))
xdict = line.new_extension_dict()
xrecord = xdict.add_xrecord("MyData")

with UserRecord(xrecord) as user_record:
    user_record.data = [  # top level has to be a list!
        "MyString",
        4711,
        3.1415,
        Vec3(1, 2, 3),
        {
            "MyIntList": [1, 2, 3],
            "MyFloatList": [4.5, 5.6, 7.8],
        },
    ]

# ------------------------------------------------------------------------------
# Example 1: Get entity specific data from the associated extension dict

if line.has_extension_dict:
    xdict = line.get_extension_dict()
    xrecord = xdict.get("MyData")
    if isinstance(xrecord, XRecord):
        user_record = UserRecord(xrecord)
        pprint(user_record.data)

# ------------------------------------------------------------------------------
# Example 2: Store arbitrary data in DICTIONARY objects.

# Get the existing DICTIONARY object or create a new DICTIONARY object:
my_dict = doc.objects.rootdict.get_required_dict("MyDict")

# Create a new XRECORD object, the DICTIONARY object is the owner of this
# new XRECORD:
xrecord = my_dict.add_xrecord("MyData")

# This example creates the user record without the context manager.
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
# Example 2: Get user data from DICTIONARY object

my_dict = doc.rootdict.get_required_dict("MyDict")
entity = my_dict["MyData"]
if isinstance(entity, XRecord):
    user_record = UserRecord(entity)
    pprint(user_record.data)

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

zoom.objects(msp, [line])
doc.saveas(DIR / "gear_with_user_data.dxf")

# ------------------------------------------------------------------------------
# Example 3: Get binary data from DICTIONARY object

entity = my_dict["MyBinaryData"]
if isinstance(entity, XRecord):
    binary_record = BinaryRecord(entity)
    print("\ncompressed data:")
    pprint(binary_record.data)

    print("\nuncompressed data:")
    pprint(zlib.decompress(binary_record.data))

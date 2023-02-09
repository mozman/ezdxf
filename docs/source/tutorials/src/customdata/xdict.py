#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

# create a DXF entity
line = msp.add_line((0, 0), (1, 0))

if line.has_extension_dict:
    # get the extension dictionary
    xdict = line.get_extension_dict()
else:
    # create a new extension dictionary
    xdict = line.new_extension_dict()

xdict.add_dictionary_var("DATA1", "Your custom data string 1")
xdict.add_dictionary_var("DATA2", "Your custom data string 2")

print(f"DATA1 is '{xdict['DATA1'].value}'")
print(f"DATA2 is '{xdict['DATA2'].value}'")


doc.saveas(DIR / "xdict.dxf")

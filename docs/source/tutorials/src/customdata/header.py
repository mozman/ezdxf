#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf
DIR = Path("~/Desktop/Outbox").expanduser()

doc = ezdxf.new()

# setting the data
doc.header["$USERI1"] = 4711
doc.header["$USERR1"] = 3.141592

# reading the data
i1 = doc.header["$USERI1"]
r1 = doc.header["$USERR1"]

# setting the data
doc.header.custom_vars.append("MyFirstVar", "First Value")

# getting the data
my_first_var = doc.header.custom_vars.get("MyFirstVar", "Default Value")

doc.saveas(DIR / "header_vars.dxf")

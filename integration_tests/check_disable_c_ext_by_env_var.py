# This test is hard to do in pytest!

import os

os.environ["EZDXF_DISABLE_C_EXT"] = "1"

import ezdxf
from ezdxf.math import Vec3
from ezdxf.math._vector import Vec3 as PythonVec3

print(f"disable C-Extension (should be True): {ezdxf.options.disable_c_ext}")
assert ezdxf.options.disable_c_ext is True

print(f"using C-Extension (should be False): {ezdxf.options.use_c_ext}")
assert ezdxf.options.use_c_ext is False

print(f"Vec3 is Python implementation (should be True): {Vec3 is PythonVec3}")
assert Vec3 is PythonVec3

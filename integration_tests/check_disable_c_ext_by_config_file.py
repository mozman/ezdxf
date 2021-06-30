# This test is hard to do in pytest!

from pathlib import Path
import ezdxf
p = Path(__file__).with_name("disable.ini")

ezdxf.options.read_file(str(p))
print(f"disable C-Extension (should be True): {ezdxf.options.disable_c_ext}")
assert ezdxf.options.disable_c_ext is True

# It is not possible to deactivate the C-extension by a user config file
# loaded after the ezdxf import, because the setup process of ezdxf is already
# finished.
print(f"using C-Extension (should be True): {ezdxf.options.use_c_ext}")
assert ezdxf.options.use_c_ext is True

#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import re
from ezdxf.tools import guid

HEX4 = "[0-9A-F]{4}"
HEX8 = "[0-9A-F]{8}"
HEX12 = "[0-9A-F]{12}"
# "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}"
AUTOCAD_PATTERN = f"{{{HEX8}-{HEX4}-{HEX4}-{HEX4}-{HEX12}}}"


def test_guid_string_matches_autocad_pattern():
    assert re.fullmatch(AUTOCAD_PATTERN, guid()) is not None


if __name__ == "__main__":
    pytest.main([__file__])

#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.tools import fonts


@pytest.fixture(scope="session", autouse=True)
def load_test_fonts():
    # Load test fonts included in the ezdxf repository:
    fonts.load_test_fonts()

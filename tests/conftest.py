#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import pytest
from ezdxf.tools import fonts
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def load_test_fonts():
    # Load test fonts included in the ezdxf repository:
    path = Path(__file__)
    font_folder = path.parent.parent / "fonts"
    if font_folder.exists():
        fonts.font_manager.clear()
        fonts.font_manager.build([str(font_folder)])
    else:
        raise SystemError(f"included test fonts not found: {str(font_folder)}")

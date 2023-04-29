#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import pytest

from ezdxf.fonts import fonts
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def load_sut_font_cache():
    path = Path(__file__)
    font_folder = path.parent.parent / "fonts"
    if font_folder.exists():
        fonts.build_sut_font_manager_cache(font_folder)
    else:
        exit(666)

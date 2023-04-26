#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import os
from pathlib import Path


# https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_sessionstart
def pytest_sessionstart(session):
    path = Path(__file__)
    font_folder = path.parent.parent / "fonts"
    if font_folder.exists():
        os.environ["EZDXF_REPO_FONTS"] = str(font_folder)

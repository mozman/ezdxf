#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import pytest

pytest.importorskip('matplotlib')

from ezdxf.tools import fonts, _matplotlib_font_support as mpl_fs

win32 = "win32"


def test_rebuild_system_fonts():
    mpl_fs._font_manager = None
    assert mpl_fs._get_font_manager() is not None


@pytest.mark.skipif(sys.platform != win32,
                    reason="requires specific Windows fonts")
def test_resolve_font_ttf_path():
    ff = fonts.get_font_face("ariblk.ttf")
    assert ff.family == "Arial"
    assert ff.weight == 900


@pytest.mark.skipif(sys.platform != win32,
                    reason="requires specific Windows fonts")
def test_font_ttf_path_from_font_face():
    # low level support
    path = mpl_fs.find_filename(family="Arial", weight=900)
    assert path.name == "ariblk.ttf"

    # high level support, see also test_resolve_font_ttf_path()
    ff = fonts.get_font_face(path.name)
    assert fonts.find_ttf_path(ff) == "ariblk.ttf"


if __name__ == '__main__':
    pytest.main([__file__])

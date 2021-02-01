#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest

pytest.importorskip('matplotlib')  # requires matplotlib!

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from ezdxf.render import path

fp = FontProperties(family='Arial')


def to_mpath(text: str):
    return TextPath((0, 0), text, size=1, prop=fp, usetex=False)


def test_curve_path_from_text_path():
    mpath = to_mpath('obc')
    paths = list(path.from_matplotlib_path(mpath))

    # Last command is a LINE_TO created by CLOSEPOLY:
    assert paths[0][-1].type == \
           path.Command.LINE_TO, "expected LINE_TO as last command"

    commands = paths[0][:-1]
    assert all((cmd.type == path.Command.CURVE3_TO
                for cmd in commands)), "expected only CURVE3_TO commands"
    assert len(paths) == 5  # 2xo 2xb 1xc


def test_line_path_from_text_path():
    mpath = to_mpath('abc')
    paths = list(path.from_matplotlib_path(mpath, curves=False))
    path0 = paths[0]
    assert all((cmd.type == path.Command.LINE_TO
                for cmd in path0)), "expected only LINE_TO commands"
    assert len(paths) == 5  # 2xa 2xb 1xc


if __name__ == '__main__':
    pytest.main([__file__])

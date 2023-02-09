# Copyright (c) 2019 Manfred Moitzi
# License: MIT License

from ezdxf.version import __version__, version


def test_version():
    assert isinstance(__version__, str)
    assert isinstance(version, tuple)

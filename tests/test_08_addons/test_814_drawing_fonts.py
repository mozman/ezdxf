#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools import fonts

# Load default font definitions, included in ezdxf:
fonts.load()


def test_find_font_without_definition():
    assert fonts.find('mozman.ttf') is None
    assert fonts.find(None) is None, "should accept None as argument"


def test_find_font_with_definition():
    assert fonts.find('arial.ttf') == (
        'arial.ttf', 'Arial', 'normal', 'normal', 400)


def test_get_font_without_definition():
    # Creates a pseudo entry:
    assert fonts.get('mozman.ttf') == (
        'mozman.ttf', 'mozman', 'normal', 'normal', 'normal'
    )
    with pytest.raises(TypeError):
        fonts.get(None)  # should not accept None as argument"


def test_get_font_with_definition():
    assert fonts.get('arial.ttf') is fonts.find('arial.ttf')


if __name__ == '__main__':
    pytest.main([__file__])

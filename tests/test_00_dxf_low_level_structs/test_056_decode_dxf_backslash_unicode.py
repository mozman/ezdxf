#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.lldxf.encoding import decode_dxf_backslash_unicode


def test_successive_chars():
    result = decode_dxf_backslash_unicode(
        r'abc\U+039B\U+0391\U+0393\U+0395\U+03A1xyz')
    assert result == r"abcΛΑΓΕΡxyz"


def test_extra_backslash():
    result = decode_dxf_backslash_unicode(
        r'abc\U+039B\\U+0391\\U+0393\\U+0395\\U+03A1xyz')
    assert result == r"abcΛ\Α\Γ\Ε\Ρxyz"


def test_extra_digits():
    result = decode_dxf_backslash_unicode(
        r'abc\U+039B0\U+03911\U+03932\U+03953\U+03A1xyz')
    assert result == r"abcΛ0Α1Γ2Ε3Ρxyz"


if __name__ == '__main__':
    pytest.main([__file__])

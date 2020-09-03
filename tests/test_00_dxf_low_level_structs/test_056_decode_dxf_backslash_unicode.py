#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.lldxf import encoding


def test_has_dxf_unicode_encoding():
    assert encoding.has_dxf_backslash_encoding(r'\U+039B') is True
    assert encoding.has_dxf_backslash_encoding(r'\\U+039B') is True
    assert encoding.has_dxf_backslash_encoding(r'\U+039') is False
    assert encoding.has_dxf_backslash_encoding(r'\U+') is False
    assert encoding.has_dxf_backslash_encoding('ABC') is False
    assert encoding.has_dxf_backslash_encoding('') is False


def test_successive_chars():
    result = encoding.decode_dxf_backslash_encoding(
        r'abc\U+039B\U+0391\U+0393\U+0395\U+03A1xyz')
    assert result == r"abcΛΑΓΕΡxyz"


def test_extra_backslash():
    result = encoding.decode_dxf_backslash_encoding(
        r'abc\U+039B\\U+0391\\U+0393\\U+0395\\U+03A1xyz')
    assert result == r"abcΛ\Α\Γ\Ε\Ρxyz"


def test_extra_digits():
    result = encoding.decode_dxf_backslash_encoding(
        r'abc\U+039B0\U+03911\U+03932\U+03953\U+03A1xyz')
    assert result == r"abcΛ0Α1Γ2Ε3Ρxyz"


if __name__ == '__main__':
    pytest.main([__file__])

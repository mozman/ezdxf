#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf


def test_has_dxf_unicode_encoding():
    assert ezdxf.has_dxf_unicode(r'\U+039B') is True
    assert ezdxf.has_dxf_unicode(r'\\U+039B') is True
    assert ezdxf.has_dxf_unicode(r'\U+039') is False
    assert ezdxf.has_dxf_unicode(r'\U+') is False
    assert ezdxf.has_dxf_unicode('ABC') is False
    assert ezdxf.has_dxf_unicode('') is False


def test_successive_chars():
    result = ezdxf.decode_dxf_unicode(
        r'abc\U+039B\U+0391\U+0393\U+0395\U+03A1xyz')
    assert result == r"abcΛΑΓΕΡxyz"


def test_extra_backslash():
    result = ezdxf.decode_dxf_unicode(
        r'abc\U+039B\\U+0391\\U+0393\\U+0395\\U+03A1xyz')
    assert result == r"abcΛ\Α\Γ\Ε\Ρxyz"


def test_extra_digits():
    result = ezdxf.decode_dxf_unicode(
        r'abc\U+039B0\U+03911\U+03932\U+03953\U+03A1xyz')
    assert result == r"abcΛ0Α1Γ2Ε3Ρxyz"


if __name__ == '__main__':
    pytest.main([__file__])

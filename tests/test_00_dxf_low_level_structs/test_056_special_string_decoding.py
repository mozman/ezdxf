#  Copyright (c) 2020-2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.lldxf.encoding import decode_mif_to_unicode, has_mif_encoding


class TestUnicodeEncoding:
    def test_has_dxf_unicode_encoding(self):
        assert ezdxf.has_dxf_unicode(r"\U+039B") is True
        assert ezdxf.has_dxf_unicode(r"\\U+039B") is True

    def test_has_not_dxf_unicode_encoding(self):
        assert ezdxf.has_dxf_unicode(r"\U+039") is False
        assert ezdxf.has_dxf_unicode(r"\U+") is False
        assert ezdxf.has_dxf_unicode("ABC") is False
        assert ezdxf.has_dxf_unicode("") is False

    def test_decode_empty_string(self):
        assert ezdxf.decode_dxf_unicode("") == ""

    def test_decode_regular_escape_sequences(self):
        assert ezdxf.decode_dxf_unicode("\n\r\t") == "\n\r\t"

    def test_decode_regular_string_without_encoding(self):
        assert ezdxf.decode_dxf_unicode("abc") == "abc"

    def test_successive_chars(self):
        result = ezdxf.decode_dxf_unicode(r"abc\U+039B\U+0391\U+0393\U+0395\U+03A1xyz")
        assert result == r"abcΛΑΓΕΡxyz"

    def test_extra_backslash(self):
        result = ezdxf.decode_dxf_unicode(
            r"abc\U+039B\\U+0391\\U+0393\\U+0395\\U+03A1xyz"
        )
        assert result == r"abcΛ\Α\Γ\Ε\Ρxyz"

    def test_extra_digits(self):
        result = ezdxf.decode_dxf_unicode(
            r"abc\U+039B0\U+03911\U+03932\U+03953\U+03A1xyz"
        )
        assert result == "abcΛ0Α1Γ2Ε3Ρxyz"


class TestMIFEncoding:
    def test_has_mif_encoding(self):
        assert has_mif_encoding(r"\M+5D7DF\M+5CFDF\M+5BCDC") is True

    def test_has_not_mif_encoding(self):
        assert has_mif_encoding(r"M+5BCDC") is False
        assert has_mif_encoding(r"\M+5BCD") is False, "5 hex digits expected"

    def test_decode_mif_encoding(self):
        assert decode_mif_to_unicode("abc") == "abc"
        assert decode_mif_to_unicode(r"\M+5D7DF\M+5CFDF\M+5BCDC") == "走线架"
        assert decode_mif_to_unicode(r"*\M+5D7DF*") == "*走*"
        assert decode_mif_to_unicode(r"\M+5D7DF\M+5CFDFM+5BCDC") == "走线M+5BCDC"

    def test_decode_empty_string(self):
        assert decode_mif_to_unicode("") == ""

    def test_decode_regular_escape_sequences(self):
        assert decode_mif_to_unicode("\n\r\t") == "\n\r\t"

    def test_decode_regular_string_without_mif_encoding(self):
        assert decode_mif_to_unicode("abc") == "abc"


if __name__ == "__main__":
    pytest.main([__file__])

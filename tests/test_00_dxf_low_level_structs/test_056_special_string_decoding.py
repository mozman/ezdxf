#  Copyright (c) 2020-2023, Manfred Moitzi
#  License: MIT License

import pytest
from io import BytesIO, StringIO
import ezdxf
from ezdxf import recover
from ezdxf.lldxf.encoding import decode_mif_to_unicode, has_mif_encoding


class TestUnicodeEncoding:
    def test_has_dxf_unicode_encoding(self):
        assert ezdxf.has_dxf_unicode(r"\U+039B") is True
        assert ezdxf.has_dxf_unicode(r"\\U+039B") is True

    def test_has_dxf_unicode_encoding_lower_case(self):
        assert ezdxf.has_dxf_unicode(r"\U+039b") is True
        assert ezdxf.has_dxf_unicode(r"\\U+039b") is True

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

    def test_successive_chars_lowercase(self):
        result = ezdxf.decode_dxf_unicode(r"abc\U+039b\U+0391\U+0393\U+0395\U+03a1xyz")
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

    def test_has_mif_encoding_lower_case(self):
        assert has_mif_encoding(r"\M+5d7df\M+5cfdf\M+5bccd") is True

    def test_has_not_mif_encoding(self):
        assert has_mif_encoding(r"M+5BCDC") is False
        assert has_mif_encoding(r"\M+5BCD") is False, "5 hex digits expected"

    def test_decode_mif_encoding(self):
        assert decode_mif_to_unicode("abc") == "abc"
        assert decode_mif_to_unicode(r"\M+5D7DF\M+5CFDF\M+5BCDC") == "走线架"
        assert decode_mif_to_unicode(r"*\M+5D7DF*") == "*走*"
        assert decode_mif_to_unicode(r"\M+5D7DF\M+5CFDFM+5BCDC") == "走线M+5BCDC"

    def test_decode_mif_encoding_lower_case(self):
        assert decode_mif_to_unicode("abc") == "abc"
        assert decode_mif_to_unicode(r"\M+5d7df\M+5cfdf\M+5bcDC") == "走线架"
        assert decode_mif_to_unicode(r"*\M+5D7df*") == "*走*"
        assert decode_mif_to_unicode(r"\M+5D7DF\M+5cFDfM+5BCdC") == "走线M+5BCdC"

    @pytest.mark.parametrize(
        "encoded, expected",
        [
            (r"\M+48861", "가"),
            (r"\M+4D065\M+48B69", "한글"),
            (r"\M+4d065\M+48b69", "한글"),
            (r"Plan: \M+48861 / \M+5D7DF", "Plan: 가 / 走"),
        ],
    )
    def test_decode_johab_mif_encoding(self, encoded, expected):
        assert decode_mif_to_unicode(encoded) == expected

    @pytest.mark.parametrize("encoded", [r"\M+4FFFF", r"\M+4886"])
    def test_invalid_johab_mif_encoding_is_preserved(self, encoded):
        assert decode_mif_to_unicode(encoded) == encoded

    def test_recover_johab_mif_text(self):
        doc = ezdxf.new("R2000")
        doc.modelspace().add_text(r"Plan: \M+48861 / \M+5D7DF")
        stream = StringIO()
        doc.write(stream)

        recovered, auditor = recover.read(BytesIO(stream.getvalue().encode("cp1252")))

        assert not auditor.errors
        assert recovered.modelspace().query("TEXT").first.dxf.text == "Plan: 가 / 走"

    def test_decode_empty_string(self):
        assert decode_mif_to_unicode("") == ""

    def test_decode_regular_escape_sequences(self):
        assert decode_mif_to_unicode("\n\r\t") == "\n\r\t"

    def test_decode_regular_string_without_mif_encoding(self):
        assert decode_mif_to_unicode("abc") == "abc"


@pytest.mark.parametrize("split", range(1, 8))
@pytest.mark.parametrize("chunk_count", [1, 2])
@pytest.mark.parametrize("unicode_prefix", [False, True])
def test_recover_mif_split_across_mtext_chunks(split, chunk_count, unicode_prefix):
    encoded = r"\M+19195"
    prefix = "x" * (250 * chunk_count - split)
    expected_prefix = prefix
    if unicode_prefix:
        prefix = r"\U+0041" + prefix[7:]
        expected_prefix = "A" + expected_prefix[7:]
    doc = ezdxf.new("R2000")
    doc.modelspace().add_mtext(prefix + encoded + encoded)
    doc.modelspace().add_text("unrelated")
    doc.modelspace().add_mtext("next entity")
    stream = StringIO()
    doc.write(stream)
    # The first escape crosses the writer's 250-character chunk boundary.
    assert encoded[:split] + "\n  1\n" + encoded[split:] in stream.getvalue()

    recovered, auditor = recover.read(BytesIO(stream.getvalue().encode("cp1252")))

    assert not auditor.errors
    assert [entity.text for entity in recovered.modelspace().query("MTEXT")] == [
        expected_prefix + "装装",
        "next entity",
    ]
    assert recovered.modelspace().query("TEXT").first.dxf.text == "unrelated"


def test_recover_mtext_with_missing_final_chunk():
    doc = ezdxf.new("R2000")
    doc.modelspace().add_mtext("x" * 250 + "tail")
    doc.modelspace().add_mtext("next entity")
    stream = StringIO()
    doc.write(stream)
    damaged = stream.getvalue().replace("  1\ntail\n", "")

    recovered, _ = recover.read(BytesIO(damaged.encode("cp1252")))

    assert [entity.text for entity in recovered.modelspace().query("MTEXT")] == [
        "x" * 250,
        "next entity",
    ]


if __name__ == "__main__":
    pytest.main([__file__])

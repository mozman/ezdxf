# Copyright (c) 2016-2021, Manfred Moitzi
# License: MIT License
import re
import codecs
import binascii

surrogate_escape = codecs.lookup_error("surrogateescape")
BACKSLASH_UNICODE = re.compile(r"(\\U\+[A-F0-9]{4})")
MIF_ENCODED = re.compile(r"(\\M\+[1-5][A-F0-9]{4})")


def dxf_backslash_replace(exc: Exception):
    if isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError)):
        s = ""
        # mypy does not recognize properties: exc.start, exc.end, exc.object
        for c in exc.object[exc.start : exc.end]:  # type: ignore
            x = ord(c)
            if x <= 0xFF:
                s += "\\x%02x" % x
            elif 0xDC80 <= x <= 0xDCFF:
                # Delegate surrogate handling:
                return surrogate_escape(exc)
            elif x <= 0xFFFF:
                s += "\\U+%04x" % x
            else:
                s += "\\U+%08x" % x
        return s, exc.end  # type: ignore
    else:
        raise TypeError(f"Can't handle {exc.__class__.__name__}")


def encode(s: str, encoding="utf8") -> bytes:
    """Shortcut to use the correct error handler"""
    return s.encode(encoding, errors="dxfreplace")


def _decode(s: str) -> str:
    if s.startswith(r"\U+"):
        return chr(int(s[3:], 16))
    else:
        return s


def has_dxf_unicode(s: str) -> bool:
    r"""Detect if string `s` contains encoded DXF unicode characters "\\U+xxxx"."""
    return bool(re.search(BACKSLASH_UNICODE, s))


def decode_dxf_unicode(s: str) -> str:
    r"""Decode DXF unicode characters "\\U+xxxx" in string `s`."""

    return "".join(_decode(part) for part in re.split(BACKSLASH_UNICODE, s))


def has_mif_encoding(s: str) -> bool:
    r"""Detect if string `s` contains encoded MIF encoded characters "\\M+cxxxx"."""
    return bool(re.search(MIF_ENCODED, s))


def decode_mif_to_unicode(s: str) -> str:
    r"""Decode MIF encoded characters "\\M+cxxxx" in string `s`."""
    return "".join(_decode_mif(part) for part in re.split(MIF_ENCODED, s))


MIF_CODE_PAGE = {
    # See https://docs.intellicad.org/files/oda/2021_11/oda_drawings_docs/frames.html?frmname=topic&frmfile=FontHandling.html
    "1": "cp932",  # Japanese (Shift-JIS)
    "2": "cp950",  # Traditional Chinese (Big 5)
    "3": "cp949",  # Wansung (KS C-5601-1987)
    "4": "cp1391",  # Johab (KS C-5601-1992)
    "5": "cp936",  # Simplified Chinese (GB 2312-80)
}


def _decode_mif(s: str) -> str:
    if s.startswith(r"\M+"):
        try:
            code_page = MIF_CODE_PAGE[s[3]]
        except KeyError:
            return s
        try:
            codec = codecs.lookup(code_page)
        except LookupError:
            return s
        try:
            byte_data = binascii.unhexlify(s[4:])
        except binascii.Error:
            return s
        try:
            return codec.decode(byte_data)[0]
        except UnicodeDecodeError:
            return s
    else:
        return s

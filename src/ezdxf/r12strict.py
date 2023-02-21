#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import string
from ezdxf import const
from ezdxf.document import Drawing


__all__ = ["translate_names", "purify", "R12NameTranslator"]


def translate_names(doc: Drawing) -> None:
    """Translate table and block names into strict DXF R12 names.

    ACAD Releases upto 14 limit names to 31 characters in length and all names are
    uppercase.  Names can include the letters A to Z, the numerals 0 to 9, and the
    special characters, dollar sign ($), underscore (_), hyphen (-) and the asterix (*).

    Most applications do not care about that and work fine with longer names and
    any characters used in names for some exceptions, but of course Autodesk
    applications are very picky about that.

    .. note::

        This is a destructive process and modifies the internals of the DXF document.

    """
    if doc.dxfversion != const.DXF12:
        raise const.DXFVersionError(
            f"expected DXF document version R12, got: {doc.acad_release}"
        )
    _R12StrictRename(doc).execute()


def purify(doc: Drawing) -> None:
    """Remove or destroy all features and entity types that are not supported by DXF
    version R12.
    """
    if doc.dxfversion != const.DXF12:
        raise const.DXFVersionError(
            f"expected DXF document version R12, got: {doc.acad_release}"
        )
    raise NotImplementedError()


class R12NameTranslator:
    """Translate table and block names into strict DXF R12 names.

    ACAD Releases upto 14 limit names to 31 characters in length and all names are
    uppercase.  Names can include the letters A to Z, the numerals 0 to 9, and the
    special characters, dollar sign ($), underscore (_), hyphen (-) and the asterix (*).

    """

    VALID_R12_NAME_CHARS = set(string.ascii_uppercase + string.digits + "$_-*")

    def __init__(self) -> None:
        self.translated_names: dict[str, str] = {}
        self.used_r12_names: set[str] = set()

    def reset(self) -> None:
        self.translated_names.clear()
        self.used_r12_names.clear()

    def translate(self, name: str) -> str:
        name = name.upper()
        r12_name = self.translated_names.get(name)
        if r12_name is None:
            r12_name = self._name_sanitizer(name, self.VALID_R12_NAME_CHARS)
            r12_name = self._get_unique_r12_name(r12_name)
            self.translated_names[name] = r12_name
        return r12_name

    def _get_unique_r12_name(self, name: str) -> str:
        name0 = name
        counter = 0
        while name in self.used_r12_names:
            ext = str(counter)
            name = name0[: (31 - len(ext))] + ext
            counter += 1
        self.used_r12_names.add(name)
        return name

    @staticmethod
    def _name_sanitizer(name: str, valid_chars: set[str]) -> str:
        # `name` has to be upper case!
        return "".join(
            (char if char in valid_chars else "_") for char in name[:31]
        )


class _R12StrictRename:
    def __init__(self, doc: Drawing) -> None:
        assert doc.dxfversion == const.DXF12, "expected DXF version R12"
        self.doc = doc
        self.translator = R12NameTranslator()

    def execute(self) -> None:
        self.rename_blocks()
        self.rename_tables()
        self.process_header_vars()
        self.process_entities()

    def rename_blocks(self) -> None:
        # - block names
        pass

    def rename_tables(self) -> None:
        # APPID name
        # DIMSTYLE name
        # - dimblk
        # - dimblk1
        # - dimblk2
        # LTYPE name
        # LAYER name
        # - linetype
        # STYLE name
        # UCS name
        # VIEW name
        # VPORT name
        pass

    def process_header_vars(self) -> None:
        # HEADER section:
        # - $CLTYPE
        # - $CLAYER
        # - $DIMBLK
        # - $DIMBLK1
        # - $DIMBLK2
        # - $DIMSTYLE
        # - $UCSNAME
        # - $PUCSNAME
        # - $TEXTSTYLE
        pass

    def process_entities(self) -> None:
        # Common graphic attributes:
        # - layer
        # - linetype
        # XDATA:
        # - 1001: APPID
        # - 1003: layer name
        #
        # TEXT
        # - text style
        # BLOCK
        # - block name
        # INSERT
        # - block name
        # ATTIB/ATTDEF
        # - tag name
        # - text style
        # VIEWPORT
        # (frozen layers XDATA 1003)
        # DIMENSION
        # - dim style
        pass

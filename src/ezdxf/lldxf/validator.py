# Copyright (C) 2018-2021, Manfred Moitzi
# License: MIT License
import logging
import io
import bisect
import math
from typing import TextIO, Iterable, List, Optional, Set, cast

from .const import (
    DXFStructureError,
    DXFError,
    DXFValueError,
    DXFAppDataError,
    DXFXDataError,
    APP_DATA_MARKER,
    HEADER_VAR_MARKER,
    XDATA_MARKER,
    INVALID_LAYER_NAME_CHARACTERS,
    acad_release,
    VALID_DXF_LINEWEIGHT_VALUES,
    VALID_DXF_LINEWEIGHTS,
    LINEWEIGHT_BYLAYER,
)

from .tagger import ascii_tags_loader
from .types import is_embedded_object_marker, DXFTag, NONE_TAG
from ezdxf.tools.codepage import toencoding
from ezdxf.math import NULLVEC

logger = logging.getLogger("ezdxf")


class DXFInfo:
    def __init__(self):
        self.release = "R12"
        self.version = "AC1009"
        self.encoding = "cp1252"
        self.handseed = "0"

    def set_header_var(self, name: str, value: str) -> int:
        if name == "$ACADVER":
            self.version = value
            self.release = acad_release.get(value, "R12")
        elif name == "$DWGCODEPAGE":
            self.encoding = toencoding(value)
        elif name == "$HANDSEED":
            self.handseed = value
        else:
            return 0
        return 1


def dxf_info(stream: TextIO) -> DXFInfo:
    info = DXFInfo()
    tagger = ascii_tags_loader(stream)
    # comments already removed
    if next(tagger) != (0, "SECTION"):
        # maybe a DXF structure error, handled by later processing
        return info
    if next(tagger) != (2, "HEADER"):
        # no leading HEADER section like DXF R12 with only ENTITIES section
        return info
    tag = NONE_TAG
    found: int = 0
    while tag != (0, "ENDSEC"):  # until end of HEADER section
        tag = next(tagger)
        if tag.code != HEADER_VAR_MARKER:
            continue
        name = cast(str, tag.value)
        value = cast(str, next(tagger).value)
        found += info.set_header_var(name, value)
        if found > 2:  # all expected values collected
            break
    return info


def header_validator(tagger: Iterable[DXFTag]) -> Iterable[DXFTag]:
    """Checks the tag structure of the content of the header section.

    Do not feed (0, 'SECTION') (2, 'HEADER') and (0, 'ENDSEC') tags!

    Args:
        tagger: generator/iterator of low level tags or compiled tags

    Raises:
        DXFStructureError() -> invalid group codes
        DXFValueError() -> invalid header variable name

    """
    variable_name_tag = True
    for tag in tagger:
        code, value = tag
        if variable_name_tag:
            if code != HEADER_VAR_MARKER:
                raise DXFStructureError(
                    f"Invalid header variable tag {code}, {value})."
                )
            if not value.startswith("$"):
                raise DXFValueError(
                    f'Invalid header variable name "{value}", missing leading "$".'
                )
            variable_name_tag = False
        else:
            variable_name_tag = True
        yield tag


def entity_structure_validator(tags: List[DXFTag]) -> Iterable[DXFTag]:
    """Checks for valid DXF entity tag structure.

    - APP DATA can not be nested and every opening tag (102, '{...') needs a
      closing tag (102, '}')
    - extended group codes (>=1000) allowed before XDATA section
    - XDATA section starts with (1001, APPID) and is always at the end of an
      entity
    - XDATA section: only group code >= 1000 is allowed
    - XDATA control strings (1002, '{') and (1002, '}') have to be balanced
    - embedded objects may follow XDATA

    XRECORD entities will not be checked.

    Args:
        tags: list of DXFTag()

    Raises:
        DXFAppDataError: for invalid APP DATA
        DXFXDataError: for invalid XDATA

    """
    assert isinstance(tags, list)
    dxftype = cast(str, tags[0].value)
    is_xrecord = dxftype == "XRECORD"
    handle: str = "???"
    app_data: bool = False
    xdata: bool = False
    xdata_list_level: int = 0
    app_data_closing_tag: str = "}"
    embedded_object: bool = False
    for tag in tags:
        if tag.code == 5 and handle == "???":
            handle = cast(str, tag.value)

        if is_embedded_object_marker(tag):
            embedded_object = True

        if embedded_object:  # no further validation
            yield tag
            continue  # with next tag

        if xdata and not embedded_object:
            if tag.code < 1000:
                dxftype = cast(str, tags[0].value)
                raise DXFXDataError(
                    f"Invalid XDATA structure in entity {dxftype}(#{handle}), "
                    f"only group code >=1000 allowed in XDATA section"
                )
            if tag.code == 1002:
                value = cast(str, tag.value)
                if value == "{":
                    xdata_list_level += 1
                elif value == "}":
                    xdata_list_level -= 1
                else:
                    raise DXFXDataError(
                        f'Invalid XDATA control string (1002, "{value}") entity'
                        f" {dxftype}(#{handle})."
                    )
                if xdata_list_level < 0:  # more closing than opening tags
                    raise DXFXDataError(
                        f"Invalid XDATA structure in entity {dxftype}(#{handle}), "
                        f'unbalanced list markers, missing  (1002, "{{").'
                    )

        if tag.code == APP_DATA_MARKER and not is_xrecord:
            # Ignore control tags (102, ...) tags in XRECORD
            value = cast(str, tag.value)
            if value.startswith("{"):
                if app_data:  # already in app data mode
                    raise DXFAppDataError(
                        f"Invalid APP DATA structure in entity {dxftype}"
                        f"(#{handle}), APP DATA can not be nested."
                    )
                app_data = True
                # 'APPID}' is also a valid closing tag
                app_data_closing_tag = value[1:] + "}"
            elif value == "}" or value == app_data_closing_tag:
                if not app_data:
                    raise DXFAppDataError(
                        f"Invalid APP DATA structure in entity {dxftype}"
                        f'(#{handle}), found (102, "}}") tag without opening tag.'
                    )
                app_data = False
                app_data_closing_tag = "}"
            else:
                raise DXFAppDataError(
                    f'Invalid APP DATA structure tag (102, "{value}") in '
                    f"entity {dxftype}(#{handle})."
                )

        # XDATA section starts with (1001, APPID) and is always at the end of
        # an entity.
        if tag.code == XDATA_MARKER and xdata is False:
            xdata = True
            if app_data:
                raise DXFAppDataError(
                    f"Invalid APP DATA structure in entity {dxftype}"
                    f'(#{handle}), missing closing tag (102, "}}").'
                )
        yield tag

    if app_data:
        raise DXFAppDataError(
            f"Invalid APP DATA structure in entity {dxftype}(#{handle}), "
            f'missing closing tag (102, "}}").'
        )
    if xdata:
        if xdata_list_level < 0:
            raise DXFXDataError(
                f"Invalid XDATA structure in entity {dxftype}(#{handle}), "
                f'unbalanced list markers, missing  (1002, "{{").'
            )
        elif xdata_list_level > 0:
            raise DXFXDataError(
                f"Invalid XDATA structure in entity {dxftype}(#{handle}), "
                f'unbalanced list markers, missing  (1002, "}}").'
            )


def is_dxf_file(filename: str) -> bool:
    """Returns ``True`` if `filename` is an ASCII DXF file."""
    with io.open(filename, errors="ignore") as fp:
        return is_dxf_stream(fp)


def is_binary_dxf_file(filename: str) -> bool:
    """Returns ``True`` if `filename` is a binary DXF file."""
    with open(filename, "rb") as fp:
        sentinel = fp.read(22)
    return sentinel == b"AutoCAD Binary DXF\r\n\x1a\x00"


def is_dwg_file(filename: str) -> bool:
    """Returns ``True`` if `filename` is a DWG file."""
    return dwg_version(filename) is not None


def dwg_version(filename: str) -> Optional[str]:
    """Returns DWG version of `filename` as string or ``None``."""
    with open(str(filename), "rb") as fp:
        try:
            version = fp.read(6).decode(errors="ignore")
        except IOError:
            return None
        if version not in acad_release:
            return None
        return version


def is_dxf_stream(stream: TextIO) -> bool:
    try:
        reader = ascii_tags_loader(stream)
    except DXFError:
        return False
    try:
        for tag in reader:
            # The common case for well formed DXF files
            if tag == (0, "SECTION"):
                return True
            # Accept/Ignore tags in front of first SECTION - like AutoCAD and
            # BricsCAD, but group code should be < 1000, until reality proofs
            # otherwise.
            if tag.code > 999:
                return False
    except DXFStructureError:
        pass
    return False


# Names used in symbol table records and in dictionaries must follow these rules:
#
# - Names can be any length in ObjectARX, but symbol names entered by users in
#   AutoCAD are limited to 255 characters.
# - AutoCAD preserves the case of names but does not use the case in
#   comparisons. For example, AutoCAD considers "Floor" to be the same symbol
#   as "FLOOR."
# - Names can be composed of all characters allowed by Windows or Mac OS for
#   filenames, except comma (,), backquote (‘), semi-colon (;), and equal
#   sign (=).
# http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-83ABF20A-57D4-4AB3-8A49-D91E0F70DBFF


def is_valid_table_name(name: str) -> bool:
    return not bool(INVALID_LAYER_NAME_CHARACTERS.intersection(set(name)))


def is_valid_layer_name(name: str) -> bool:
    if is_adsk_special_layer(name):
        return True
    else:
        return is_valid_table_name(name)


def is_adsk_special_layer(name: str) -> bool:
    if name.startswith("*"):
        # special Autodesk layers starts with invalid character *
        name = name.upper()
        if name.startswith("*ADSK_"):
            return True
        if name.startswith("*ACMAP"):
            return True
        if name.startswith("*TEMPORARY"):
            return True
    return False


def is_valid_block_name(name: str) -> bool:
    if name.startswith("*"):
        return is_valid_table_name(name[1:])
    else:
        return is_valid_table_name(name)


def is_valid_vport_name(name: str) -> bool:
    if name.startswith("*"):
        return name.upper() == "*ACTIVE"
    else:
        return is_valid_table_name(name)


def is_valid_lineweight(lineweight: int) -> bool:
    return lineweight in VALID_DXF_LINEWEIGHT_VALUES


def fix_lineweight(lineweight: int) -> int:
    if lineweight in VALID_DXF_LINEWEIGHT_VALUES:
        return lineweight
    if lineweight < -3:
        return LINEWEIGHT_BYLAYER
    if lineweight > 211:
        return 211
    index = bisect.bisect(VALID_DXF_LINEWEIGHTS, lineweight)
    return VALID_DXF_LINEWEIGHTS[index]


def is_valid_aci_color(aci: int) -> bool:
    return 0 <= aci <= 257


def is_in_integer_range(start: int, end: int):
    """Range of integer values, excluding the `end` value."""

    def _validator(value: int) -> bool:
        return start <= value < end

    return _validator


def fit_into_integer_range(start: int, end: int):
    def _fixer(value: int) -> int:
        return min(max(value, start), end - 1)

    return _fixer


def fit_into_float_range(start: float, end: float):
    def _fixer(value: float) -> float:
        return min(max(value, start), end)

    return _fixer


def is_in_float_range(start: float, end: float):
    """Range of float values, including the `end` value."""

    def _validator(value: float) -> bool:
        return start <= value <= end

    return _validator


def is_not_null_vector(v) -> bool:
    return not NULLVEC.isclose(v)


def is_not_zero(v: float) -> bool:
    return not math.isclose(v, 0.0, abs_tol=1e-12)


def is_not_negative(v) -> bool:
    return v >= 0


is_greater_or_equal_zero = is_not_negative


def is_positive(v) -> bool:
    return v > 0


is_greater_zero = is_positive


def is_valid_bitmask(mask: int):
    def _validator(value: int) -> bool:
        return not bool(~mask & value)

    return _validator


def fix_bitmask(mask: int):
    def _fixer(value: int) -> int:
        return mask & value

    return _fixer


def is_integer_bool(v) -> bool:
    return v in (0, 1)


def fix_integer_bool(v) -> int:
    return 1 if v else 0


def is_one_of(values: Set):
    def _validator(v) -> bool:
        return v in values

    return _validator


def is_valid_one_line_text(text: str) -> bool:
    has_line_breaks = bool(set(text).intersection({"\n", "\r"}))
    return not has_line_breaks and not text.endswith("^")


def fix_one_line_text(text: str) -> str:
    return text.replace("\n", "").replace("\r", "").rstrip("^")


def is_valid_attrib_tag(tag: str) -> bool:
    return is_valid_one_line_text(tag)


def fix_attrib_tag(tag: str) -> str:
    return fix_one_line_text(tag)


def is_handle(handle) -> bool:
    try:
        int(handle, 16)
    except (ValueError, TypeError):
        return False
    return True

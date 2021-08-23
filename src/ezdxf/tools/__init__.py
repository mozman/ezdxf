# Copyright (c) 2015-2021, Manfred Moitzi
# License: MIT License
from typing import Tuple, Any, Iterable
from uuid import uuid4
import functools
import html
from .juliandate import juliandate, calendardate
from .binarydata import hex_strings_to_bytes, bytes_to_hexstr

escape = functools.partial(html.escape, quote=True)


def float2transparency(value: float) -> int:
    """
    Returns DXF transparency value as integer in the range from ``0`` to ``255``, where ``0`` is 100% transparent
    and ``255`` is opaque.

    Args:
        value: transparency value as float in the range from ``0`` to ``1``, where ``0`` is opaque
               and ``1`` is 100% transparency.

    """
    return int((1.0 - float(value)) * 255) | 0x02000000


def transparency2float(value: int) -> float:
    """
    Returns transparency value as float from ``0`` to ``1``, ``0`` for no transparency (opaque) and ``1``
    for 100% transparency.

    Args:
        value: DXF integer transparency value, ``0`` for 100% transparency and ``255`` for opaque

    """
    # 255 -> 0.
    # 0 -> 1.
    return 1.0 - float(int(value) & 0xFF) / 255.0


def set_flag_state(flags: int, flag: int, state: bool = True) -> int:
    """Set/clear binary `flag` in data `flags`.

    Args:
        flags: data value
        flag: flag to set/clear
        state: ``True`` for setting, ``False`` for clearing

    """
    if state:
        flags = flags | flag
    else:
        flags = flags & ~flag
    return flags


def guid() -> str:
    """Returns a general unique ID, based on :func:`uuid.uuid4`.

    This function creates a GUID for the header variables $VERSIONGUID and
    $FINGERPRINTGUID, which matches the AutoCAD pattern
    ``{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}``.

    """
    return "{" + str(uuid4()).upper() + "}"


def take2(iterable: Iterable) -> Iterable[Tuple[Any, Any]]:
    """Iterate `iterable` as 2-tuples.

    :code:`[1, 2, 3, 4, ...] -> (1, 2), (3, 4), ...`

    """
    store = None
    for item in iterable:
        if store is None:
            store = item
        else:
            yield store, item
            store = None


def suppress_zeros(s: str, leading: bool = False, trailing: bool = True):
    """Suppress trailing and/or leading ``0`` of string `s`.

    Args:
         s: data string
         leading: suppress leading ``0``
         trailing: suppress trailing ``0``

    """
    # is anything to do?
    if (not leading) and (not trailing):
        return s

    # if `s` represents zero
    if float(s) == 0.0:
        return "0"

    # preserve sign
    if s[0] in "-+":
        sign = s[0]
        s = s[1:]
    else:
        sign = ""

    # strip zeros
    if leading:
        s = s.lstrip("0")
    if trailing:
        s = s.rstrip("0")

    # remove comma if no decimals follow
    if s[-1] in ".,":
        s = s[:-1]

    return sign + s


def normalize_text_angle(angle: float, fix_upside_down=True) -> float:
    """
    Normalizes text `angle` to the range from 0 to 360 degrees and fixes upside down text angles.

    Args:
        angle: text angle in degrees
        fix_upside_down: rotate upside down text angle about 180 degree

    """
    angle = angle % 360.0  # normalize angle (0 .. 360)
    if fix_upside_down and (90 < angle <= 270):  # flip text orientation
        angle -= 180
        angle = angle % 360.0  # normalize again
    return angle

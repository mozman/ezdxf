#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
"""
This module manages a backend agnostic font database.

Weight Values: https://developer.mozilla.org/de/docs/Web/CSS/font-weight

Supported by matplotlib, pyqt, SVG

=========== =====
Thin        100
Hairline    100
ExtraLight  200
UltraLight  200
Light       300
Normal      400
Medium      500
DemiBold    600
SemiBold    600
Bold        700
ExtraBold   800
UltraBold   800
Black       900
Heavy       900
ExtraBlack  950
UltraBlack  950
=========== =====

Stretch Values: https://developer.mozilla.org/en-US/docs/Web/CSS/font-stretch

Supported by matplotlib, SVG

=============== ======
ultra-condensed 50%
extra-condensed 62.5%
condensed       75%
semi-condensed  87.5%
normal          100%
semi-expanded   112.5%
expanded        125%
extra-expanded  150%
ultra-expanded  200%
=============== ======

"""
from typing import Dict, Optional, NamedTuple
import abc
import logging
from pathlib import Path
import json
from ezdxf import options

FONT_FACE_CACHE_FILE = "font_face_cache.json"
FONT_MEASUREMENT_CACHE_FILE = "font_measurement_cache.json"
logger = logging.getLogger("ezdxf")


class FontFace(NamedTuple):
    # This would be the matplotlib FontProperties class, if matplotlib would
    # be a core dependency!
    ttf: str = ""
    family: str = "sans-serif"
    style: str = "normal"
    stretch: str = "normal"
    weight: str = "normal"

    @property
    def is_italic(self) -> bool:
        return self.style.find("italic") > -1

    @property
    def is_oblique(self) -> bool:
        return self.style.find("oblique") > -1

    @property
    def is_bold(self) -> bool:
        weight = self.weight
        if isinstance(weight, str):
            weight = weight_name_to_value(weight)  # type: ignore
        return weight > 400  # type: ignore


# Key is TTF font file name without path in lowercase like "arial.ttf":
font_face_cache: Dict[str, FontFace] = dict()
font_measurement_cache: Dict[str, "FontMeasurements"] = dict()

WEIGHT_TO_VALUE = {
    "thin": 100,
    "hairline": 100,
    "extralight": 200,
    "UltraLight": 200,
    "light": 300,
    "normal": 400,
    "medium": 500,
    "demibold": 600,
    "semibold": 600,
    "bold": 700,
    "extrabold": 800,
    "ultrabold": 800,
    "black": 900,
    "heavy": 900,
    "extrablack": 950,
    "ultrablack": 950,
}

SHX_FONTS = {
    # See examples in: CADKitSamples/Shapefont.dxf
    # Shape file structure is not documented, therefore replace this fonts by
    # true type fonts.
    # `None` is for: use the default font.
    #
    # All these replacement TTF fonts have a copyright remark:
    # "(c) Copyright 1996 by Autodesk Inc., All rights reserved"
    # and therefore can not be included in ezdxf or the associated repository!
    # You got them if you install any Autodesk product, like the free available
    # DWG/DXF viewer "TrueView" : https://www.autodesk.com/viewers
    "AMGDT": "amgdt___.ttf",  # Tolerance symbols
    "AMGDT.SHX": "amgdt___.ttf",
    "COMPLEX": "complex_.ttf",
    "COMPLEX.SHX": "complex_.ttf",
    "ISOCP": "isocp.ttf",
    "ISOCP.SHX": "isocp.ttf",
    "ITALIC": "italicc_.ttf",
    "ITALIC.SHX": "italicc_.ttf",
    "GOTHICG": "gothicg_.ttf",
    "GOTHICG.SHX": "gothicg_.ttf",
    "GREEKC": "greekc.ttf",
    "GREEKC.SHX": "greekc.ttf",
    "ROMANS": "romans__.ttf",
    "ROMANS.SHX": "romans__.ttf",
    "SCRIPTS": "scripts_.ttf",
    "SCRIPTS.SHX": "scripts_.ttf",
    "SCRIPTC": "scriptc_.ttf",
    "SCRIPTC.SHX": "scriptc_.ttf",
    "SIMPLEX": "simplex_.ttf",
    "SIMPLEX.SHX": "simplex_.ttf",
    "SYMATH": "symath__.ttf",
    "SYMATH.SHX": "symath__.ttf",
    "SYMAP": "symap___.ttf",
    "SYMAP.SHX": "symap___.ttf",
    "SYMETEO": "symeteo_.ttf",
    "SYMETEO.SHX": "symeteo_.ttf",
    "TXT": "txt_____.ttf",  # Default AutoCAD font
    "TXT.SHX": "txt_____.ttf",
}
TTF_TO_SHX = {v: k for k, v in SHX_FONTS.items() if k.endswith("SHX")}
DESCENDER_FACTOR = 0.333  # from TXT SHX font - just guessing
X_HEIGHT_FACTOR = 0.666  # from TXT SHX font - just guessing


def map_shx_to_ttf(font_name: str) -> str:
    """Map SHX font names to TTF file names. e.g. "TXT" -> "txt_____.ttf" """
    # Map SHX fonts to True Type Fonts:
    font_upper = font_name.upper()
    if font_upper in SHX_FONTS:
        font_name = SHX_FONTS[font_upper]
    return font_name


def map_ttf_to_shx(ttf: str) -> Optional[str]:
    """Map TTF file names to SHX font names. e.g. "txt_____.ttf" -> "TXT" """
    return TTF_TO_SHX.get(ttf.lower())


def weight_name_to_value(name: str) -> int:
    """Map weight names to values. e.g. 'normal' -> 400"""
    return WEIGHT_TO_VALUE.get(name.lower(), 400)


def cache_key(name: str) -> str:
    """Returns the normalize TTF file name in lower case without preceding
    folders. e.g. "C:\\Windows\\Fonts\\Arial.TTF" -> "arial.ttf"
    """
    return Path(name).name.lower()


def build_system_font_cache(*, path=None, rebuild=True) -> None:
    """Build system font cache and save it to directory `path` if given.
    Set `rebuild` to ``False`` to just add new fonts.
    Requires the Matplotlib package!

    A rebuild has to be done only after a new ezdxf installation, or new fonts
    were added to your system (which you want to use), or an update of ezdxf if
    you don't use your own external font cache directory.

    See also: :attr:`ezdxf.options.font_cache_directory`

    """
    try:
        from ._matplotlib_font_support import (
            load_system_fonts,
            build_font_measurement_cache,
            remove_fonts_without_measurement,
            reset_font_manager,
        )
    except ImportError:
        logger.debug("This function requires the optional Matplotlib package.")
        return

    global font_face_cache, font_measurement_cache
    if rebuild:
        reset_font_manager()
    cache = load_system_fonts()
    if rebuild:
        font_face_cache = cache
    else:
        font_face_cache.update(cache)

    if rebuild:
        font_measurement_cache = dict()
    # else update existing measurement cache:
    font_measurement_cache = build_font_measurement_cache(
        font_face_cache, font_measurement_cache
    )
    # Fonts without a measurement can not be processed and should be replaced
    # by a default font:
    remove_fonts_without_measurement(font_face_cache, font_measurement_cache)
    # save caches on default location defined by option.font_cache_directory:
    save(path)


def find_font_face(ttf_path: Optional[str]) -> Optional[FontFace]:
    """Get cached font face definition by TTF file name e.g. "Arial.ttf",
    returns ``None`` if not found.

    """
    if ttf_path:
        return font_face_cache.get(cache_key(ttf_path))
    else:
        return None


def get_font_face(ttf_path: str, map_shx=True) -> FontFace:
    """Get cached font face definition by TTF file name e.g. "Arial.ttf".

    This function translates a DXF font definition by
    the raw TTF font file name into a :class:`FontFace` object. Fonts which are
    not available on the current system gets a default font face.

    Args:
        ttf_path: raw font file name as stored in the
            :class:`~ezdxf.entities.Textstyle` entity
        map_shx: maps SHX font names to TTF replacement fonts,
            e.g. "TXT" -> "txt_____.ttf"

    """
    if not isinstance(ttf_path, str):
        raise TypeError("ttf_path has invalid type")
    if map_shx:
        ttf_path = map_shx_to_ttf(ttf_path)
    font = find_font_face(ttf_path)
    if font is None:
        # Create a pseudo entry:
        name = cache_key(ttf_path)
        return FontFace(
            name,
            Path(ttf_path).stem,
            "normal",
            "normal",
            "normal",
        )
    else:
        return font


def get_font_measurements(ttf_path: str, map_shx=True) -> "FontMeasurements":
    """Get cached font measurements by TTF file name e.g. "Arial.ttf".

    Args:
        ttf_path: raw font file name as stored in the
            :class:`~ezdxf.entities.Textstyle` entity
        map_shx: maps SHX font names to TTF replacement fonts,
            e.g. "TXT" -> "txt_____.ttf"

    """
    # TODO: is using freetype-py the better solution?
    if map_shx:
        ttf_path = map_shx_to_ttf(ttf_path)
    m = font_measurement_cache.get(cache_key(ttf_path))
    if m is None:
        m = FontMeasurements(
            baseline=0,
            cap_height=1,
            x_height=X_HEIGHT_FACTOR,
            descender_height=DESCENDER_FACTOR,
        )
    return m


def find_font_face_by_family(
    family: str, italic=False, bold=False
) -> Optional["FontFace"]:
    # TODO: find best match
    #  additional attributes "italic" and "bold" are ignored yet
    key = family.lower()
    for f in font_face_cache.values():
        if key == f.family.lower():
            return f
    return None


def find_ttf_path(font_face: FontFace, default="DejaVuSans.ttf") -> str:
    """Returns the true type font path."""
    if options.use_matplotlib:
        from ._matplotlib_font_support import find_filename

        path = find_filename(
            family=font_face.family,
            style=font_face.style,
            stretch=font_face.stretch,
            weight=font_face.weight,
        )
        return path.name
    else:
        font_face = find_font_face_by_family(  # type: ignore
            font_face.family,
            italic=font_face.is_italic,
            bold=font_face.is_bold,
        )
        return default if font_face is None else font_face.ttf


def get_cache_file_path(path, name: str = FONT_FACE_CACHE_FILE) -> Path:
    """Build path to cache files."""
    if path is None and options.font_cache_directory:
        directory = options.font_cache_directory.strip('"')
        path = Path(directory).expanduser()
        path.mkdir(exist_ok=True)
    path = Path(path) if path else Path(__file__).parent
    return path.expanduser() / name


def load(path=None, reload=False):
    """Load all caches from given `path` or from default location, defined by
    :attr:`ezdxf.options.font_cache_directory` or the default cache from
    the ``ezdxf.tools`` folder.

    This function is called automatically at startup if not disabled by
    environment variable ``EZDXF_AUTO_LOAD_FONTS``.

    """
    global font_face_cache, font_measurement_cache

    if len(font_face_cache) and reload is False:
        return  # skip if called multiple times:
    p = get_cache_file_path(path, FONT_FACE_CACHE_FILE)
    if p.exists():
        font_face_cache = _load_font_faces(p)
    p = get_cache_file_path(path, FONT_MEASUREMENT_CACHE_FILE)
    if p.exists():
        font_measurement_cache = _load_measurement_cache(p)


def _load_font_faces(path) -> Dict:
    """Load font face cache."""
    with open(path, "rt") as fp:
        data = json.load(fp)
    cache = dict()
    if data:
        for entry in data:
            key = entry[0]
            cache[key] = FontFace(*entry)
    return cache


def _load_measurement_cache(path) -> Dict:
    """Load font measurement cache."""
    with open(path, "rt") as fp:
        data = json.load(fp)
    cache = dict()
    if data:
        for entry in data:
            key = entry[0]
            cache[key] = FontMeasurements(*entry[1])
    return cache


def save(path=None):
    """Save all caches to given `path` or to default location, defined by
    options.font_cache_directory or into the ezdxf.tools folder.

    """
    if path:
        Path(path).expanduser().mkdir(parents=True, exist_ok=True)
    p = get_cache_file_path(path, FONT_FACE_CACHE_FILE)
    with open(p, "wt") as fp:
        json.dump(list(font_face_cache.values()), fp, indent=2)

    p = get_cache_file_path(path, FONT_MEASUREMENT_CACHE_FILE)
    with open(p, "wt") as fp:
        json.dump(list(font_measurement_cache.items()), fp, indent=2)


# A Visual Guide to the Anatomy of Typography: https://visme.co/blog/type-anatomy/
# Anatomy of a Character: https://www.fonts.com/content/learning/fontology/level-1/type-anatomy/anatomy


class FontMeasurements(NamedTuple):
    baseline: float
    cap_height: float
    x_height: float
    descender_height: float

    def scale(self, factor: float = 1.0) -> "FontMeasurements":
        return FontMeasurements(
            self.baseline * factor,
            self.cap_height * factor,
            self.x_height * factor,
            self.descender_height * factor,
        )

    def shift(self, distance: float = 0.0) -> "FontMeasurements":
        return FontMeasurements(
            self.baseline + distance,
            self.cap_height,
            self.x_height,
            self.descender_height,
        )

    def scale_from_baseline(
        self, desired_cap_height: float
    ) -> "FontMeasurements":
        factor = desired_cap_height / self.cap_height
        return FontMeasurements(
            self.baseline,
            desired_cap_height,
            self.x_height * factor,
            self.descender_height * factor,
        )

    @property
    def cap_top(self) -> float:
        return self.baseline + self.cap_height

    @property
    def x_top(self) -> float:
        return self.baseline + self.x_height

    @property
    def bottom(self) -> float:
        return self.baseline - self.descender_height

    @property
    def total_height(self) -> float:
        return self.cap_height + self.descender_height


class AbstractFont:
    def __init__(self, measurements: FontMeasurements):
        self.measurements = measurements

    @abc.abstractmethod
    def text_width(self, text: str) -> float:
        pass

    @abc.abstractmethod
    def space_width(self) -> float:
        pass


class MatplotlibFont(AbstractFont):
    """This class provides proper font measurement support by using the optional
    Matplotlib font support.

    Use the :func:`make_font` factory function to create a font abstraction.

    """

    def __init__(
        self, ttf_path: str, cap_height: float = 1.0, width_factor: float = 1.0
    ):
        from . import _matplotlib_font_support

        self._support_lib = _matplotlib_font_support
        # unscaled font measurement:
        font_measurements = get_font_measurements(ttf_path)
        super().__init__(font_measurements.scale_from_baseline(cap_height))
        font_face = get_font_face(ttf_path)
        scale = cap_height / font_measurements.cap_height
        self._font_properties = self._support_lib.get_font_properties(font_face)
        self._width_factor = width_factor * scale
        self._space_width = self.text_width(" X") - self.text_width("X")

    def text_width(self, text: str) -> float:
        """Returns the text with in drawing units for the given `text` string.
        Text rendering and width calculation is done by the Matplotlib
        :class:`TextPath` class.

        """
        if not text.strip():
            return 0
        path = self._support_lib.get_text_path(text, self._font_properties)
        try:
            return max(path.vertices[:, 0].tolist()) * self._width_factor
        except RuntimeError as e:
            logger.error(f"Matplotlib RuntimeError: {str(e)}")
            return 0

    def space_width(self) -> float:
        """Returns the width of a "space" char."""
        return self._space_width


class MonospaceFont(AbstractFont):
    """Defines a monospaced font without knowing the real font properties.
    Each letter has the same cap- and descender height and the same width.
    This font abstraction is used if no Matplotlib font support is available.

    Use the :func:`make_font` factory function to create a font abstraction.

    """

    def __init__(
        self,
        cap_height: float,
        width_factor: float = 1.0,
        baseline: float = 0,
        descender_factor: float = DESCENDER_FACTOR,
        x_height_factor: float = X_HEIGHT_FACTOR,
    ):
        super().__init__(
            FontMeasurements(
                baseline=baseline,
                cap_height=cap_height,
                x_height=cap_height * x_height_factor,
                descender_height=cap_height * descender_factor,
            )
        )
        self._width_factor: float = abs(width_factor)
        self._space_width = self.measurements.cap_height * self._width_factor

    def text_width(self, text: str) -> float:
        """Returns the text width in drawing units for the given `text` based
        on a simple monospaced font calculation.

        """
        return len(text) * self.measurements.cap_height * self._width_factor

    def space_width(self) -> float:
        """Returns the width of a "space" char."""
        return self._space_width


def make_font(
    ttf_path: str, cap_height: float, width_factor: float = 1.0
) -> AbstractFont:
    """Factory function to create a font abstraction.

    Creates a :class:`MatplotlibFont` if the Matplotlib font support is
    available and enabled or else a :class:`MonospaceFont`.

    Args:
        ttf_path: raw font file name as stored in the
            :class:`~ezdxf.entities.Textstyle` entity
        cap_height: desired cap height in drawing units.
        width_factor: horizontal text stretch factor

    """
    if options.use_matplotlib:
        return MatplotlibFont(ttf_path, cap_height, width_factor)
    else:
        return MonospaceFont(cap_height, width_factor)

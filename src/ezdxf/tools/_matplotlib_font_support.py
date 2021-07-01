# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Optional, Dict
from pathlib import Path
from functools import lru_cache
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontManager
from . import fonts

_font_manager: Optional[FontManager] = None


def reset_font_manager() -> None:
    global _font_manager
    _font_manager = FontManager()


def _get_font_manager() -> FontManager:
    if _font_manager is None:
        reset_font_manager()
    assert _font_manager is not None
    return _font_manager


def load_system_fonts() -> Dict[str, fonts.FontFace]:
    """Load system fonts by the FontManager of matplotlib.

    This may take a long time!

    """
    font_faces = dict()
    fm = _get_font_manager()
    for entry in fm.ttflist:
        ttf = fonts.cache_key(entry.fname)
        font_faces[ttf] = fonts.FontFace(
            ttf,
            entry.name,
            entry.style,
            entry.stretch,
            entry.weight,
        )
    return font_faces


@lru_cache(maxsize=256)
def get_font_properties(font_face: fonts.FontFace) -> FontProperties:
    """Returns a matplotlib :class:`FontProperties` object."""
    font_properties = FontProperties()
    if font_face:
        try:
            font_properties = FontProperties(
                family=font_face.family,
                style=font_face.style,
                stretch=font_face.stretch,
                weight=font_face.weight,
            )
        except ValueError:
            pass
    return font_properties


def get_font_measurements(
    font_face: fonts.FontFace,
) -> Optional[fonts.FontMeasurements]:
    """Returns :class:`FontMeasurement` object, calculated by matplotlib.

    Returns ``None`` if the font can't be processed.

    """
    if font_face is None:
        raise TypeError("invalid font_face")
    font_properties = get_font_properties(font_face)
    try:
        # TODO: xmin, ymin, xmax, ymax = TextPath.get_extends()?
        upper_x = get_text_path("X", font_properties).vertices[:, 1].tolist()
        lower_x = get_text_path("x", font_properties).vertices[:, 1].tolist()
        lower_p = get_text_path("p", font_properties).vertices[:, 1].tolist()
    except RuntimeError:
        print(f"Runtime error processing font: {font_properties.get_name()}")
        return None
    baseline = min(lower_x)
    measurements = fonts.FontMeasurements(
        baseline=baseline,
        cap_height=max(upper_x) - baseline,
        x_height=max(lower_x) - baseline,
        descender_height=baseline - min(lower_p),
    )
    return measurements


def get_text_path(text: str, font: FontProperties, size=1) -> TextPath:
    """Returns a matplotlib :class:`TextPath` object."""
    return TextPath(
        (0, 0), text.replace("$", "\\$"), size=size, prop=font, usetex=False
    )


def build_font_measurement_cache(
    font_faces: Dict[str, fonts.FontFace],
    measurements: Dict[str, fonts.FontMeasurements],
) -> Dict[str, fonts.FontMeasurements]:
    """Build font measurement cache for all known TTF fonts."""
    for ttf_path, font_face in font_faces.items():
        if ttf_path not in measurements:
            measurement = get_font_measurements(font_face)
            if measurement is not None:
                measurements[ttf_path] = measurement
    return measurements


def remove_fonts_without_measurement(font_faces: Dict, measurements: Dict):
    """Remove fonts without a measurement from `font_faces` which can not be
    processed and should be replaced by a default font.
    """
    names = list(font_faces.keys())
    for name in names:
        if name not in measurements:
            del font_faces[name]


def find_filename(
    family: str,
    style: str = "normal",
    stretch: str = "normal",
    weight: str = "normal",
) -> Path:
    fm = _get_font_manager()
    prop = FontProperties(
        family=family, style=style, stretch=stretch, weight=weight
    )
    return Path(fm.findfont(prop))

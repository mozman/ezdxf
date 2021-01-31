# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Optional, Dict
from functools import lru_cache
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontManager
from . import fonts

# load font face- and font measurement cache included in ezdxf:
fonts.load()


def load_system_fonts() -> Dict[str, fonts.FontFace]:
    # This is not done automatically, because this may take a long
    # time and is not important for every user.
    font_faces = dict()
    for entry in FontManager().ttflist:
        ttf = fonts.db_key(entry.fname)
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
        font_properties: FontProperties) -> Optional[fonts.FontMeasurements]:
    if font_properties is None:
        raise TypeError('invalid font_properties')
    try:
        upper_x = get_text_path('X', font_properties).vertices[:, 1].tolist()
        lower_x = get_text_path('x', font_properties).vertices[:, 1].tolist()
        lower_p = get_text_path('p', font_properties).vertices[:, 1].tolist()
    except RuntimeError:
        print(f'Runtime error processing font: {font_properties.get_name()}')
        return None
    baseline = min(lower_x)
    measurements = fonts.FontMeasurements(
        baseline=baseline,
        cap_height=max(upper_x) - baseline,
        x_height=max(lower_x) - baseline,
        descender_height=baseline - min(lower_p)
    )
    return measurements


def get_text_path(text: str, font: FontProperties) -> TextPath:
    return TextPath((0, 0), text.replace('$', '\\$'), size=1, prop=font,
                    usetex=False)


def build_font_measurement_cache(
        font_faces: Dict[str, fonts.FontFace],
        measurements: Dict[str, fonts.FontMeasurements],
    ) -> Dict[str, fonts.FontMeasurements]:
    """ Build font measurement cache for all known TTF fonts.

    This measurements are stored in a global cache file. Building this cache is
    only necessary if new fonts are added. e.g. add_system_fonts()

    """
    for ttf_path, font_face in font_faces.items():
        if ttf_path not in measurements:
            font_properties = get_font_properties(font_face)
            measurement = get_font_measurements(font_properties)
            if measurement is not None:
                measurements[ttf_path] = measurement
    return measurements


def remove_fonts_without_measurement(font_faces: Dict, measurements: Dict):
    names = list(font_faces.keys())
    for name in names:
        if name not in measurements:
            del font_faces[name]

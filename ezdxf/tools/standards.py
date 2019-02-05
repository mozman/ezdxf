# Purpose: Define standard linetypes, text styles
# Created: 23.03.2016
# Copyright (c) 2016-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Tuple, Sequence, Union, cast
from ezdxf.render.arrows import ARROWS
from ezdxf.options import options
import logging

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes import Drawing, DimStyle

logger = logging.getLogger('ezdxf')


def setup_drawing(dwg: 'Drawing', topics: Union[str, bool, Sequence] = 'all'):
    if not topics:  # topics is None, False or ''
        return

    def get_token(name: str) -> List[str]:
        for t in topics:
            token = t.split(':')
            if token[0] == name:
                return token
        return []

    if topics in ('all', True):
        setup_all = True
        topics = []
    else:
        setup_all = False
        topics = list(t.lower() for t in topics)

    if setup_all or 'linetypes' in topics:
        setup_linetypes(dwg)

    if setup_all or 'styles' in topics:
        setup_styles(dwg)

    dimstyles = get_token('dimstyles')
    if setup_all or len(dimstyles):
        if len(dimstyles) == 2:
            domain = dimstyles[1]
        else:
            domain = 'all'
        setup_dimstyles(dwg, domain=domain)


def setup_linetypes(dwg: 'Drawing') -> None:
    for name, desc, pattern in linetypes():
        if name in dwg.linetypes:
            continue
        dwg.linetypes.new(name, dxfattribs={
            'description': desc,
            'pattern': pattern,
        })


def setup_styles(dwg: 'Drawing') -> None:
    dwg.header['$TEXTSTYLE'] = 'OpenSans'
    for name, font in styles():
        if name in dwg.styles:
            continue
        dwg.styles.new(name, dxfattribs={
            'font': font,
        })


def setup_dimstyles(dwg: 'Drawing', domain: str = 'all') -> None:
    setup_styles(dwg)
    setup_dimstyle(dwg, name='EZDXF', fmt='EZ_M_100_H25_CM', style=options.default_dimension_text_style,
                   blk=ARROWS.architectural_tick)
    dwg.header['$DIMSTYLE'] = 'EZDXF'
    if domain in ('metric', 'all'):
        setup_dimstyle(dwg, fmt='EZ_M_100_H25_CM', style=options.default_dimension_text_style)
        setup_dimstyle(dwg, fmt='EZ_M_50_H25_CM', style=options.default_dimension_text_style)
        setup_dimstyle(dwg, fmt='EZ_M_25_H25_CM', style=options.default_dimension_text_style)
        setup_dimstyle(dwg, fmt='EZ_M_20_H25_CM', style=options.default_dimension_text_style)
        setup_dimstyle(dwg, fmt='EZ_M_10_H25_CM', style=options.default_dimension_text_style)
        setup_dimstyle(dwg, fmt='EZ_M_5_H25_CM', style=options.default_dimension_text_style)
        setup_dimstyle(dwg, fmt='EZ_M_1_H25_CM', style=options.default_dimension_text_style)


class DimStyleFmt:
    DIMASZ = .25
    DIMTSZ = .125
    UNIT_FACTOR = {
        'm': 1,  # 1 drawing unit == 1 meter
        'dm': 10,  # 1 drawing unit == 1 decimeter
        'cm': 100,  # 1 drawing unit == 1 centimeter
        'mm': 1000,  # 1 drawing unit == 1 millimeter
    }

    def __init__(self, fmt: str):
        tokens = fmt.lower().split('_')
        self.name = fmt
        self.drawing_unit = tokens[1]  # EZ_<M>_100_H25_CM
        self.scale = float(tokens[2])  # EZ_M_<100>_H25_CM
        self.height = float(tokens[3][1:]) / 10.  # EZ_M_100_H<25>_CM  # in mm
        self.measurement_unit = tokens[4]  # EZ_M_100_H25_<CM>

    @property
    def unit_factor(self):
        return self.UNIT_FACTOR[self.drawing_unit]

    @property
    def measurement_factor(self):
        return self.UNIT_FACTOR[self.measurement_unit]

    @property
    def text_factor(self):
        return self.unit_factor / self.UNIT_FACTOR['mm']

    @property
    def dimlfac(self):
        return self.measurement_factor / self.unit_factor

    @property
    def dimasz(self):
        return self.DIMASZ * self.unit_factor

    @property
    def dimtxt(self):
        return self.height * self.text_factor * self.scale

    @property
    def dimexe(self):
        return self.dimtxt * 1.5

    @property
    def dimexo(self):
        return self.dimtxt / 2

    @property
    def dimdle(self):
        return .25 * self.unit_factor

    @property
    def dimtsz(self):
        return self.DIMTSZ * self.unit_factor


def setup_dimstyle(dwg: 'Drawing', fmt: str, style: str = None, blk: str = None, name: str = '') -> 'DimStyle':
    """
    Easy DimStyle setup, the `fmt` string defines four essential dimension parameters separated by the `_` character.
    Tested and works with the metric system, I don't touch the 'english unit' system.

    Example: `fmt` = 'EZ_M_100_H25_CM'

        1. '<EZ>_M_100_H25_CM': arbitrary prefix
        2. 'EZ_<M>_100_H25_CM': defines the drawing unit, valid values are 'M', 'DM', 'CM', 'MM'
        3. 'EZ_M_<100>_H25_CM': defines the scale of the drawing, '100' is for 1:100
        4. 'EZ_M_100_<H25>_CM': defines the text height in mm in paper space times 10, 'H25' is 2.5mm
        5. 'EZ_M_100_H25_<CM>': defines the units for the measurement text, valid values are 'M', 'DM', 'CM', 'MM'

    Args:
        dwg: DXF drawing
        fmt: format string
        style: text style for measurement
        blk: block name for arrow None for oblique stroke
        name: dimension style name, if name is '', `fmt` string is used as name

    """
    style = style or options.default_dimension_text_style
    fmt = DimStyleFmt(fmt)
    name = name or fmt.name
    if dwg.dimstyles.has_entry(name):
        logging.debug('DimStyle "{}" already exists.'.format(name))
        return cast('DimStyle', dwg.dimstyles.get(name))

    dimstyle = cast('DimStyle', dwg.dimstyles.new(name))
    dimstyle.dxf.dimtxt = fmt.dimtxt
    dimstyle.dxf.dimlfac = fmt.dimlfac  # factor for measurement; dwg in m : measurement in cm -> dimlfac=100
    dimstyle.dxf.dimgap = fmt.dimtxt * .4  # gap between text and dimension line
    dimstyle.dxf.dimtad = 1  # text above dimline
    dimstyle.dxf.dimexe = fmt.dimexe
    dimstyle.dxf.dimexo = fmt.dimexo
    dimstyle.dxf.dimdle = 0  # dimension extension beyond extension lines
    dimstyle.dxf.dimtix = 0  # Draws dimension text between the extension lines even if it would ordinarily be placed outside those lines
    dimstyle.dxf.dimtih = 0  # Aligns text inside extension lines with dimension line; 1 = Draws text horizontally
    dimstyle.dxf.dimtoh = 0  # Aligns text outside of extension lines with dimension line; 1 = Draws text horizontally
    dimstyle.dxf.dimzin = 8  # Suppresses trailing zeros in decimal dimensions
    dimstyle.dxf.dimsah = 0
    if blk is None:  # oblique stroke
        dimstyle.dxf.dimtsz = fmt.dimtsz
    else:  # arrow or block
        dimstyle.set_arrows(blk=blk)
        dimstyle.dxf.dimasz = fmt.dimasz  # tick factor
    if dwg.dxfversion > 'AC1009':
        # set text style
        dimstyle.dxf.dimtxsty = style
        dimstyle.dxf.dimupt = 1  # user location override, controls both the text position and the dimension line location, same as DXF12
        dimstyle.dxf.dimdsep = ord('.')
    return dimstyle


def linetypes() -> List[Tuple[str, str, Sequence[float]]]:
    """ Creates a list of standard line types.
    """
    # dxf linetype definition
    # name, description, elements:
    # elements = [total_pattern_length, elem1, elem2, ...]
    # total_pattern_length = sum(abs(elem))
    # elem > 0 is line, < 0 is gap, 0.0 = dot;
    return [("CONTINUOUS", "Solid", [0.0]),
            ("CENTER", "Center ____ _ ____ _ ____ _ ____ _ ____ _ ____",
             [2.0, 1.25, -0.25, 0.25, -0.25]),
            ("CENTERX2", "Center (2x) ________  __  ________  __  ________",
             [3.5, 2.5, -0.25, 0.5, -0.25]),
            ("CENTER2", "Center (.5x) ____ _ ____ _ ____ _ ____ _ ____",
             [1.0, 0.625, -0.125, 0.125, -0.125]),
            ("DASHED", "Dashed __ __ __ __ __ __ __ __ __ __ __ __ __ _",
             [0.6, 0.5, -0.1]),
            ("DASHEDX2", "Dashed (2x) ____  ____  ____  ____  ____  ____",
             [1.2, 1.0, -0.2]),
            ("DASHED2", "Dashed (.5x) _ _ _ _ _ _ _ _ _ _ _ _ _ _",
             [0.3, 0.25, -0.05]),
            ("PHANTOM", "Phantom ______  __  __  ______  __  __  ______",
             [2.5, 1.25, -0.25, 0.25, -0.25, 0.25, -0.25]),
            ("PHANTOMX2", "Phantom (2x)____________    ____    ____    ____________",
             [4.25, 2.5, -0.25, 0.5, -0.25, 0.5, -0.25]),
            ("PHANTOM2", "Phantom (.5x) ___ _ _ ___ _ _ ___ _ _ ___ _ _ ___",
             [1.25, 0.625, -0.125, 0.125, -0.125, 0.125, -0.125]),
            ("DASHDOT", "Dash dot __ . __ . __ . __ . __ . __ . __ . __",
             [1.4, 1.0, -0.2, 0.0, -0.2]),
            ("DASHDOTX2", "Dash dot (2x) ____  .  ____  .  ____  .  ____",
             [2.4, 2.0, -0.2, 0.0, -0.2]),
            ("DASHDOT2", "Dash dot (.5x) _ . _ . _ . _ . _ . _ . _ . _",
             [0.7, 0.5, -0.1, 0.0, -0.1]),
            ("DOT", "Dot .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .",
             [0.2, 0.0, -0.2]),
            ("DOTX2", "Dot (2x) .    .    .    .    .    .    .    . ",
             [0.4, 0.0, -0.4]),
            ("DOT2", "Dot (.5) . . . . . . . . . . . . . . . . . . . ",
             [0.1, 0.0, -0.1]),
            ("DIVIDE", "Divide __ . . __ . . __ . . __ . . __ . . __",
             [1.6, 1.0, -0.2, 0.0, -0.2, 0.0, -0.2]),
            ("DIVIDEX2", "Divide (2x) ____  . .  ____  . .  ____  . .  ____",
             [2.6, 2.0, -0.2, 0.0, -0.2, 0.0, -0.2]),
            ("DIVIDE2", "Divide(.5x) _ . _ . _ . _ . _ . _ . _ . _",
             [0.8, 0.5, -0.1, 0.0, -0.1, 0.0, -0.1]),
            ]


def styles():
    """ Creates a list of standard styles.
    """
    return [
        ('STANDARD', 'txt'),
        ('OpenSans-Light', 'OpenSans-Light.ttf'),
        ('OpenSans-Light-Italic', 'OpenSans-LightItalic.ttf'),
        ('OpenSans', 'OpenSans-Regular.ttf'),
        ('OpenSans-Italic', 'OpenSans-Italic.ttf'),
        ('OpenSans-SemiBold', 'OpenSans-SemiBold.ttf'),
        ('OpenSans-SemiBoldItalic', 'OpenSans-SemiBoldItalic.ttf'),
        ('OpenSans-Bold', 'OpenSans-Bold.ttf'),
        ('OpenSans-BoldItalic', 'OpenSans-BoldItalic.ttf'),
        ('OpenSans-ExtraBold', 'OpenSans-ExtraBold.ttf'),
        ('OpenSans-ExtraBoldItalic', 'OpenSans-ExtraBoldItalic.ttf'),
        ('OpenSansCondensed-Bold', 'OpenSansCondensed-Bold.ttf'),
        ('OpenSansCondensed-Light', 'OpenSansCondensed-Light.ttf'),
        ('OpenSansCondensed-Italic', 'OpenSansCondensed-LightItalic.ttf'),
        ('LiberationSans', 'LiberationSans-Regular.ttf'),
        ('LiberationSans-Bold', 'LiberationSans-Bold.ttf'),
        ('LiberationSans-BoldItalic', 'LiberationSans-BoldItalic.ttf'),
        ('LiberationSans-Italic', 'LiberationSans-Italic.ttf'),
        ('LiberationSerif', 'LiberationSerif-Regular.ttf'),
        ('LiberationSerif-Bold', 'LiberationSerif-Bold.ttf'),
        ('LiberationSerif-BoldItalic', 'LiberationSerif-BoldItalic.ttf'),
        ('LiberationSerif-Italic', 'LiberationSerif-Italic.ttf'),
        ('LiberationMono', 'LiberationMono-Regular.ttf'),
        ('LiberationMono-Bold', 'LiberationMono-Bold.ttf'),
        ('LiberationMono-BoldItalic', 'LiberationMono-BoldItalic.ttf'),
        ('LiberationMono-Italic', 'LiberationMono-Italic.ttf'),
    ]

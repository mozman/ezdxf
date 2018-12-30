# Purpose: Define standard linetypes, text styles
# Created: 23.03.2016
# Copyright (c) 2016-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Tuple, Sequence, Union, cast
from ezdxf.lldxf.const import DEFAULT_DIM_TEXT_STYLE, EZTICK, EZBULLET
import logging

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes import Drawing, DimStyle

logger = logging.getLogger('ezdxf')


def setup_drawing(dwg: 'Drawing', topics: Union[str, Sequence] = 'all'):
    if not topics:  # topics is None, False or ''
        return

    def get_token(name: str) -> List[str]:
        for t in topics:
            token = t.split(':')
            if token[0] == name:
                return token
        return []

    if topics == 'all':
        setup_all = True
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
    for name, font in styles():
        if name in dwg.styles:
            continue
        dwg.styles.new(name, dxfattribs={
            'font': font,
        })


def setup_dimension_ticks(dwg: 'Drawing') -> None:
    # ticks scaled for 1:1 drawing unit = 1 m
    # tick size on paper 5x5mm
    def add_cross(block, size=(1., 1.)):
        h, v = size
        h = h / 2
        v = v / 2
        block.add_line((-h, 0), (h, 0), dxfattribs=cross_attribs)
        block.add_line((0, -v), (0, v), dxfattribs=cross_attribs)

    cross_attribs = {}
    tick_attribs = {}
    if dwg.dxfversion > 'AC1009':
        cross_attribs['lineweight'] = 18
        tick_attribs['lineweight'] = 35

    if EZBULLET not in dwg.blocks:
        blk = dwg.blocks.new(EZBULLET)
        add_cross(blk, size=(.005, .005))
        blk.add_circle(center=(0, 0), radius=.001, dxfattribs=tick_attribs)

    if EZTICK not in dwg.blocks:
        blk = dwg.blocks.new(EZTICK)
        add_cross(blk, size=(.0025, .005))
        s2 = .0025/2.
        blk.add_line((-s2, -s2), (s2, s2), dxfattribs=tick_attribs)


LENGTH_FACTOR = {
    'm': 1,
    'dm': 10,
    'cm': 100,
    'mm': 1000,
}

UNIT_FACTOR = {
    'm': 1,  # 1 drawing unit == 1 meter
    'dm': 10,  # 1 drawing unit == 1 decimeter
    'cm': 100,  # 1 drawing unit == 1 centimeter
    'mm': 1000,  # 1 drawing unit == 1 millimeter
}


def setup_dimstyles(dwg: 'Drawing', domain: str = 'all') -> None:
    setup_styles(dwg)
    setup_dimension_ticks(dwg)
    setup_dimstyle(dwg, name='EZDXF', fmt='EZ_M_100_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)

    if domain == 'metric':
        setup_dimstyle(dwg, fmt='EZ_M_100_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)
        setup_dimstyle(dwg, fmt='EZ_M_50_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)
        setup_dimstyle(dwg, fmt='EZ_M_25_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)
        setup_dimstyle(dwg, fmt='EZ_M_20_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)
        setup_dimstyle(dwg, fmt='EZ_M_10_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)
        setup_dimstyle(dwg, fmt='EZ_M_5_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)
        setup_dimstyle(dwg, fmt='EZ_M_1_H25_CM', style=DEFAULT_DIM_TEXT_STYLE)


class DimStyleFmt:
    def __init__(self, fmt: str):
        tokens = fmt.lower().split('_')
        self.name = fmt
        self.unit = tokens[1]  # EZ_<M>_100_H25_CM
        self.scale = float(tokens[2])  # EZ_M_<100>_H25_CM
        self.height = float(tokens[3][1:]) / 10.  # EZ_M_100_H<25>_CM  # in mm
        self.length_factor = LENGTH_FACTOR[tokens[4]]  # EZ_M_100_H25_<CM>


def setup_dimstyle(dwg: 'Drawing', fmt: str, style: str = 'OPEN SANS', tick: str = 'EZTICK', name: str = '') -> None:
    fmt = DimStyleFmt(fmt)
    name = name or fmt.name
    if dwg.dimstyles.has_entry(name):
        logging.debug('DimStyle "{}" already exists.'.format(name))
        return

    unit_factor = UNIT_FACTOR[fmt.unit]
    dimstyle = cast('DimStyle', dwg.dimstyles.new(name))
    txt_height_in_dwg_units = fmt.height / UNIT_FACTOR['mm']  # fmt.height is in mm e.g. H25 = 2.5mm
    dimstyle.dxf.dimtxt = txt_height_in_dwg_units * fmt.scale
    dimstyle.dxf.dimlfac = fmt.length_factor  # factor for measurement; dwg in m : measurement in cm -> dimlfac=100
    dimstyle.dxf.dimasz = (fmt.scale * unit_factor)  # tick factor
    dimstyle.dxf.dimgap = dimstyle.dxf.dimtxt * .2  # text above dimline
    dimstyle.set_ticks(blk=tick)
    if dwg.dxfversion > 'AC1009':
        # set text style
        dimstyle.dxf.dimtxsty = style


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
        ('STANDARD', 'arial.ttf'),
        ('ARIAL', 'arial.ttf'),
        ('ARIAL_NARROW', 'arialn.ttf'),
        ('ISOCPEUR', 'isocpeur.ttf'),
        ('OPEN_SANS', 'Open Sans'),
        ('OPEN_SANS_BOLD', 'Open Sans Bold'),
        ('OPEN_SANS_CONDENSED_BOLD', 'Open Sans Condensed'),
        ('OPEN_SANS_CONDENSED_LIGHT', 'Open Sans Condensed Light'),
        ('TIMES', 'times.ttf'),
    ]

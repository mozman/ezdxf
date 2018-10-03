# Purpose: Define standard linetypes, text styles
# Created: 23.03.2016
# Copyright (c) 2016-2018, Manfred Moitzi
# License: MIT License


def setup_linetypes(dwg):
    for name, desc, pattern in linetypes():
        if name in dwg.linetypes:
            continue
        dwg.linetypes.new(name, dxfattribs={
            'description': desc,
            'pattern': pattern,
        })


def setup_styles(dwg):
    for name, font in styles():
        if name in dwg.styles:
            continue
        dwg.styles.new(name, dxfattribs={
            'font': font,
        })


def linetypes():
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
        ('TIMES', 'times.ttf'),
    ]

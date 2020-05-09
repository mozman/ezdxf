# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
"""
CIRCLE    Layer: "LAYER-5"
Color: 5 (blue)    Linetype: "BYLAYER"
center point, (-9.56460754, 8.44764172, 9.97894327)

CIRCLE    Layer: "LAYER-4"
Color: 4 (cyan)    Linetype: "BYLAYER"
center point, (-1.60085321, 9.29648008, 1.85322122)

CIRCLE    Layer: "LAYER-3"
Color: 3 (green)    Linetype: "BYLAYER"
center point, (-3.56027455, 9.08762984, 3.85249348)

CIRCLE    Layer: "LAYER-2"
Color: 2 (yellow)    Linetype: "BYLAYER"
center point, (-5.53851623, 8.87677359, 5.87096886)

Extrusion direction relative to UCS: X=0.70819791  Y=0.07548520  Z=0.70196702

"""
from ezdxf.math import OCS, Matrix44, Matrix33, Vector

EXTRUSION = (0.7081979129501316, 0.0754851955385861, 0.7019670229772758)


def is_close_points(p1, p2, places=6):
    for v1, v2 in zip(p1, p2):
        if not round(v1, places) == round(v2, places):
            return False
    return True


def test_wcs_to_ocs():
    ocs = OCS(EXTRUSION)
    assert is_close_points(
        ocs.from_wcs((-9.56460754, 8.44764172, 9.97894327)),
        (9.41378764657076, 13.15481838975576, 0.8689258932616031),
        places=6,
    )
    assert is_close_points(
        ocs.from_wcs((-1.60085321, 9.29648008, 1.85322122)),
        (9.41378764657076, 1.745643639268379, 0.8689258932616031),
        places=6,
    )
    assert is_close_points(
        ocs.from_wcs((-3.56027455, 9.08762984, 3.85249348)),
        (9.41378764657076, 4.552784531093068, 0.8689258932616031),
        places=6,
    )
    assert is_close_points(
        ocs.from_wcs((-5.53851623, 8.87677359, 5.87096886)),
        (9.41378764657076, 7.386888158025531, 0.8689258932616031),
        places=6,
    )


def test_ocs_to_wcs():
    ocs = OCS(EXTRUSION)
    wcs = ocs.to_wcs((9.41378764657076, 13.15481838975576, 0.8689258932616031))
    assert is_close_points(
        wcs,
        (-9.56460754, 8.44764172, 9.97894327),
        places=6,
    )
    assert is_close_points(
        ocs.to_wcs((9.41378764657076, 1.745643639268379, 0.8689258932616031)),
        (-1.60085321, 9.29648008, 1.85322122),
        places=6,
    )
    assert is_close_points(
        ocs.to_wcs((9.41378764657076, 4.552784531093068, 0.8689258932616031)),
        (-3.56027455, 9.08762984, 3.85249348),
        places=6,
    )
    assert is_close_points(
        ocs.to_wcs((9.41378764657076, 7.386888158025531, 0.8689258932616031)),
        (-5.53851623, 8.87677359, 5.87096886),
        places=6,
    )


def test_matrix44_to_ocs():
    ocs = OCS(EXTRUSION)
    matrix = Matrix44.ucs(ocs.ux, ocs.uy, ocs.uz)
    assert is_close_points(
        matrix.ocs_from_wcs(Vector(-9.56460754, 8.44764172, 9.97894327)),
        (9.41378764657076, 13.15481838975576, 0.8689258932616031),
        places=6,
    )


def test_matrix44_to_wcs():
    ocs = OCS(EXTRUSION)
    matrix = Matrix44.ucs(ocs.ux, ocs.uy, ocs.uz)
    assert is_close_points(
        matrix.ocs_to_wcs(Vector(9.41378764657076, 13.15481838975576, 0.8689258932616031)),
        (-9.56460754, 8.44764172, 9.97894327),
        places=6,
    )


def test_matrix33_determinant():
    m = Matrix33((1, 14, 31), (2, -6, -1), (0, 8, 15))
    assert m.determinant() == -6

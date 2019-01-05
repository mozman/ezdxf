# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from ezdxf.units import DrawingUnits, PaperSpaceUnits
from math import isclose


def test_msp_1_m():
    # 1 drawing unit = 1 m
    u = DrawingUnits(1, 'm')
    assert 7*u('m') == 7, "should be 7 drawing units"
    # rounding errors!
    assert isclose(7*u('dm'), .7), "should be 0.7 drawing units"
    assert 7*u('cm') == .07, "should be 0.07 drawing units"
    assert 7*u('mm') == .007, "should be 0.007 drawing units"
    assert 7*u('km') == 7000, "should be 7000 drawing units"
    assert isclose(7*u('ft'), 2.1336), "should be 2.1336 drawing units"
    assert isclose(70*u('in'), 1.778), "should be 1.778 drawing units"
    assert isclose(7*u('yd'), 6.4008), "should be 6.4008 drawing units"


def test_msp_easy_usage():
    u = DrawingUnits(1, 'm')
    cm = u('cm')
    assert 100*cm == 1


def test_msp_2_m():
    # 1 drawing unit = 2 m
    u = DrawingUnits(2, 'm')
    assert 1*u('m') == 2, "should be 2 drawing units"
    assert 7*u('m') == 14, "should be 14 drawing units"
    assert 7*u('cm') == 0.14, "should be 0.14 drawing units"
    assert 7*u('mm') == 0.014, "should be 0.014 drawing units"
    assert 7*u('km') == 14000, "should be 14000 drawing units"


def test_msp_1_ft():
    # 1 drawing unit = 1 ft
    u = DrawingUnits(1, 'ft')
    assert isclose(1*u('ft'), 1), "should be 1 drawing unit"
    assert isclose(10*u('yd'), 30), "should be 30 drawing unit"
    assert isclose(100*u('in'), 8.3333333333), "should be 8.33333 drawing unit"
    assert round(u('mi')) == 5280, "should be 5280 drawing unit"
    assert isclose(100*u('m'), 328.0839895), "should be 328.084 drawing unit"
    assert isclose(u('km'), 3280.839895), "should be 3280.8399 drawing unit"


def test_msp_2_ft():
    # 1 drawing unit = 2 ft
    u = DrawingUnits(2, 'ft')
    assert isclose(1*u('ft'), 2), "should be 2 drawing unit"
    assert isclose(10*u('yd'), 60), "should be 60 drawing unit"


def test_msp_1_in():
    # 1 drawing unit = 1 in
    u = DrawingUnits(1, 'in')
    assert isclose(1*u('ft'), 12), "should be 12 drawing units"
    assert isclose(1*u('yd'), 36), "should be 36 drawing units"
    assert round(u('mi')) == 63360, "should be 63360 drawing units"
    assert isclose(100*u('m'), 3937.007874), "should be 3937.0079 drawing units"
    assert isclose(u('km'), 39370.07874)
    assert isclose(100*u('dm'), 393.7007874)
    assert isclose(100*u('cm'), 39.37007874)
    assert isclose(100*u('mm'), 3.937007874)
    assert isclose(100*u('µm'), 0.003937007874)


def test_paper_space_scale_1_1():
    psu = PaperSpaceUnits(DrawingUnits(1, 'm'), unit='mm', scale=1.)
    assert psu.from_msp(1, 'm') == 1000, 'should be 1000 mm in paper space'
    assert psu.from_msp(10, 'cm') == 100
    assert psu.from_msp(10, 'mm') == 10

    psu = PaperSpaceUnits(DrawingUnits(1, 'yd'), unit='in', scale=1.)
    assert round(psu.from_msp(1, 'yd')) == 36, 'should be 36 inch in paper space'
    assert round(psu.from_msp(1, 'ft')) == 12, 'should be 12 inch in paper space'


def test_paper_space_scale_1_100():
    psu = PaperSpaceUnits(DrawingUnits(1, 'm'), unit='mm', scale=100.)
    assert psu.from_msp(1, 'm') == 10, '1m in msp, should be 10 mm in paper space 1:100'
    assert psu.from_msp(500, 'cm') == 50

    psu = PaperSpaceUnits(DrawingUnits(1, 'yd'), unit='in', scale=100.)
    assert round(psu.from_msp(1, 'yd'), 2) == .36, '1 yd in msp, should be .36 inch in paper space 1:100'
    assert round(psu.from_msp(1, 'ft'), 2) == .12, '1 ft in msp,should be .12 inch in paper space 1:100'


def test_paper_space_default():
    # Default: 1 drawing unit = 1 m, paperspace units = 'mm', scale = 1:1
    psu = PaperSpaceUnits()
    assert psu.from_msp(1, 'm') == 1000

    psu = PaperSpaceUnits(scale=100)
    assert psu.from_msp(1, 'm') == 10


def test_paper_space_to_model_space_metric():
    psu = PaperSpaceUnits(msp=DrawingUnits(1, 'm'), scale=100)
    assert psu.to_msp(10, 'mm') == 1, '1mm in PSP 1:100 => should be 1 drawing unit in model space'
    assert psu.to_msp(5, 'cm') == 5, '5cm in PSP 1:100 => should be 5 drawing unit in model space'


def test_paper_space_to_model_space_us():
    psu = PaperSpaceUnits(msp=DrawingUnits(1, 'yd'), scale=100)
    assert isclose(psu.to_msp(1, 'in'), 2.77777777777), '1 inch in PSP 1:100 => should be 2.777 drawing unit in model space'



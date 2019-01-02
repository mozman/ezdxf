from ezdxf.tools import raise_decimals


def test_lift_decimals():
    assert raise_decimals('123.23') == '123²³'
    assert raise_decimals('123.5') == '123\u2075'
    assert raise_decimals('123.') == '123'
    assert raise_decimals('123') == '123'
    assert raise_decimals('123.2 0.2') == '123² 0²'


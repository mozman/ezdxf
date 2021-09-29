# Purpose: test dxfvalue
# Created: 12.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from ezdxf.sections.header import HeaderVar


class TestDXFValue:
    def test_single_value_code(self):
        var = HeaderVar((0, "SECTION"))
        assert 0 == var.code

    def test_single_value_value(self):
        var = HeaderVar((0, "SECTION"))
        assert "SECTION" == var.value

    def test_single_value_str(self):
        var = HeaderVar((0, "SECTION"))
        assert "  0\nSECTION\n" == str(var)

    def test_not_ispoint(self):
        var = HeaderVar((0, "SECTION"))
        assert var.ispoint is False

    def test_ispoint(self):
        var = HeaderVar((10, (1, 1)))
        assert var.ispoint is True

    def test__point_2coords(self):
        var = HeaderVar((10, (1, 1)))
        assert (1, 1) == var.value

    def test_point_3coords(self):
        var = HeaderVar((10, (1, 2, 3)))
        assert (1, 2, 3) == var.value

    def test_point_str(self):
        var = HeaderVar((10, (1, 2, 3)))
        assert " 10\n1\n 20\n2\n 30\n3\n" == str(var)

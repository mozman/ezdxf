# Copyright (c) 2021 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entities.text import Text


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
class TestDeprecatedMethodsStillWork:
    @pytest.fixture
    def text(self):
        return Text.new(handle="ABBA", owner="0")

    def test_get_align_enum(self, text):
        text.dxf.halign = 1
        text.dxf.valign = 3
        assert text.get_align() == "TOP_CENTER"

    def test_get_pos_TOP_CENTER(self, text):
        text.set_pos((2, 2), align="TOP_CENTER")
        align, p1, p2 = text.get_pos()
        assert align == "TOP_CENTER"
        assert p1 == (2, 2)
        assert p2 is None

    def test_set_alignment(self, text):
        text.set_pos((2, 2), align="TOP_CENTER")
        assert text.dxf.halign == 1
        assert text.dxf.valign == 3
        assert text.dxf.align_point == (2, 2)

    def test_set_fit_alignment(self, text):
        text.set_pos((2, 2), (4, 2), align="FIT")
        assert text.dxf.halign == 5
        assert text.dxf.valign == 0
        assert text.dxf.insert == (2, 2)
        assert text.dxf.align_point == (4, 2)

#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import shapefile


class TestFontShapeFile:
    @pytest.fixture(scope="class")
    def txt(self):
        return shapefile.shp_loads(TXT)

    def test_shape_file_name(self, txt):
        assert txt.name == "TXT"

    def test_cap_height(self, txt):
        assert txt.cap_height == 6

    def test_descender(self, txt):
        assert txt.descender == 2

    def test_mode(self, txt):
        assert txt.mode == shapefile.FontMode.BIDIRECT

    def test_encoding(self, txt):
        assert txt.encoding == shapefile.FontEncoding.UNICODE

    def test_embed(self, txt):
        assert txt.embed == shapefile.FontEmbedding.ALLOWED

    def test_is_font(self, txt):
        assert txt.is_font is True

    def test_shape_count(self, txt):
        assert len(txt) == 5

    def test_shape_by_number(self, txt):
        assert txt[32].name == "spc"

    def test_find_shape_by_name(self, txt):
        assert txt.find("spc").number == 32

    def test_find_undefined_shape(self, txt):
        assert txt.find("undefined") is None


class TestShapeFile:
    """Any shape file without a font definition is a common shape file"""
    @pytest.fixture(scope="class")
    def shp(self):
        return shapefile.shp_loads(FILE_1)

    def test_is_a_shape_file(self, shp):
        assert shp.is_shape_file is True

    def test_shape_by_number(self, shp):
        assert shp[0x53].name == "S"

    def test_shape_by_name(self, shp):
        assert shp.find("S").number == 0x53


FILE_1 = """
*00053,37,S
2,8,(24,36),1,12,(-10,2,12),3,10,4,2,12,(-18,-76,100),8,(56,-28),
12,(-18,-76,-100),4,10,3,2,12,(-12,4,-18),2,8,(26,-6),0
"""

TXT = """

;;type, size, name
*UNIFONT,6,TXT
;;above, below, mode, encode, embed, 0
6,2,2,0,0,0

;;shapenumber, defbytes, shapename
*0000A,7,lf
2,0AC,14,8,(9,10),0

*00020,7,spc
2,060,14,8,(-6,-8),0

*00041,21,uca
2,14,8,(-2,-6),1,024,043,04D,02C,2,047,1,040,2,02E,14,8,(-4,-3),
0

*00042,29,ucb
2,14,8,(-2,-6),1,030,012,014,016,028,2,020,1,012,014,016,038,2,
010,1,06C,2,050,14,8,(-4,-3),0

*00043,23,ucc
2,14,8,(-2,-6),040,014,1,01A,028,016,044,012,020,01E,2,02E,03C,
14,8,(-4,-3),0

"""

if __name__ == "__main__":
    pytest.main([__file__])

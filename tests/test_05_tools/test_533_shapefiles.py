#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import shapefile, path


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


class TestShapeRenderer:
    @pytest.fixture(scope="class")
    def shp(self):
        return shapefile.shp_loads(FILE_1)

    def test_render_only_lines(self, shp):
        p = shp.render_shape(0x41)  # uppercase letter A
        commands = p.commands()
        assert [c.type for c in commands] == [
            path.Command.LINE_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
        ]
        assert p.start.isclose((6, 2))
        assert p.end.isclose((36, 0))

    def test_render_bulges(self, shp):
        p = shp.render_shape(0x53)  # uppercase letter S
        commands = p.commands()
        assert [c.type for c in commands] == [
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
        ]
        assert p.start.isclose((24, 36))
        assert p.end.isclose((32, 0))
        curve3 = commands[2]
        assert curve3[0].isclose((10.400000000000002, 22.8))
        assert curve3[1].isclose((5.3604119976499085, 28.205904025073004))
        assert curve3[2].isclose((7.089973469642831, 24.478591646965565))

        curve5 = commands[4]
        assert curve5[0].isclose((25.784251968503938, 8.182677165354324))
        assert curve5[1].isclose((24.910026530357175, 15.52140835303443))
        assert curve5[2].isclose((26.6395880023501, 11.794095974926988))

    def test_render_full_circle_by_octant_arc(self, shp):
        p = shp.render_shape(0x38)  # number 8
        commands = p.commands()
        assert [c.type for c in commands] == [
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
        ]
        assert p.start.isclose((14, 22))
        assert p.end.isclose((28, 0))

    def test_render_fractional_octant_arcs(self, shp):
        p = shp.render_shape(0x26)  # number &
        commands = p.commands()
        assert [c.type for c in commands] == [
            path.Command.LINE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
        ]
        assert p.start.isclose((30, 14))
        assert p.end.isclose((35.592878624100585, 0.6236849533424156))


FILE_1 = """
*00026,41,&
2,8,(30,14),1,3,10,4,2,8,(-72,-54),3,2,12,(-89,76,-102),4,4,
8,(31,45),3,4,4,10,11,(68,187,0,6,076),8,(17,-27),2,8,(10,-2),0

*00038,24,8
2,8,(14,22),1,10,(8,060),2,08A,1,10,(8,-044),04C,10,(8,-004),044,
2,8,(22,-14),0

*00041,28,A
2,8,(6,2),1,8,(12,36),8,(12,-36),3,2,2,8,(-7,20),1,8,(-34,0),2,
8,(53,-24),4,2,0

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

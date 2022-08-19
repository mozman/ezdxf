#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf import shapefile, path


def test_filter_noise():
    lines = list(
        shapefile.filter_noise(
            """
    ;; comment
    
    *BIGFONT xxx, 234
    
    
    """.split(
                "\n"
            )
        )
    )
    assert lines[0].startswith("*BIGFONT") is True


def test_merge_wrapped_spec_line():
    lines = list(
        shapefile.merge_lines(
            shapefile.filter_noise(
                """*000BB
,25,NAME
2,8,(6,4),1,8,(6,10),8,(-6,10),2,0C0,1,8,(6,-10),8,(-6,-10),2,
8,(12,-4),0
    """.split(
                    "\n"
                )
            )
        )
    )
    assert len(lines) == 2
    assert lines[0] == "*000BB,25,NAME"
    assert len(lines[1]) == 73


def test_do_not_merge_spec_without_name():
    lines = list(
        shapefile.merge_lines(
            shapefile.filter_noise(
                """*00025,29,
2,8,(6,2),1,8,(32,36),2,8,(-20,-6),1,10,(6,000),2,8,(8,-24),1,
10,(6,040),2,8,(18,-8),0
    """.split(
                    "\n"
                )
            )
        )
    )
    assert len(lines) == 2
    assert lines[0] == "*00025,29,"
    assert len(lines[1]) == 86


def test_big_font_not_supported():
    with pytest.raises(shapefile.UnsupportedShapeFile):
        shapefile.shp_loads(
            """
*BIGFONT 7392,3,081,09F,0E0,0EA,0FD,0FE
*0,5,Comment
15,0,2,14,0
        """
        )


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

    def test_render_ccw_fractional_arcs_number_nine(self, shp):
        # This has the correct continuation
        p = shp.render_text("9")
        commands = p.commands()
        assert [c.type for c in commands] == [
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
        ]
        assert p.start.isclose((10, 2))
        # solved by a hack:
        assert abs(p.end.y) < 1e-9, "has to be on the baseline"

        p = shp.render_shape(0x39)
        assert p.end.isclose(
            (28.144414741079267, 0.020931856849379926)
        ), "fractional arc rendering solved?"

    def test_render_ccw_fractional_arcs_ampersand(self, shp):
        p = shp.render_text("&")
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
        # solved by a hack:
        assert abs(p.end.y) < 1e-9, "has to be on the baseline"

        p = shp.render_shape(0x26)
        assert p.end.isclose(
            (36.031289001494976, -0.1845547786548103)
        ), "fractional arc rendering solved?"

    def test_render_clockwise_fractional_arcs_letter_c(self, shp):
        p = shp.render_text("C")  # bold.shp
        commands = p.commands()
        assert [c.type for c in commands] == [
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.LINE_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
            path.Command.CURVE4_TO,
            path.Command.CURVE4_TO,
            path.Command.MOVE_TO,
        ]
        assert p.start.isclose((-2, 30))
        p2 = shp.render_shape(0x43)
        assert p2.end.isclose((64, 0))
        assert p2.end.isclose(
            p.end
        ), "should be perfect rendering - no placing-hack required"


FILE_1 = """
;; isocp.shp
*00026,41,&
2,8,(30,14),1,3,10,4,2,8,(-72,-54),3,2,12,(-89,76,-102),4,4,
8,(31,45),3,4,4,10,11,(68,187,0,6,076),8,(17,-27),2,8,(10,-2),0

;; isocp.shp
*00038,24,8
2,8,(14,22),1,10,(8,060),2,08A,1,10,(8,-044),04C,10,(8,-004),044,
2,8,(22,-14),0

;; isocp.shp
*00039,25,9
2,8,(10,2),1,11,(108,0,0,18,062),0B4,10,(8,004),04C,10,(8,042),
080,2,8,(6,-18),0

;; isocp.shp
*00041,28,A
2,8,(6,2),1,8,(12,36),8,(12,-36),3,2,2,8,(-7,20),1,8,(-34,0),2,
8,(53,-24),4,2,0

;; bold.shp
*00043,156,C
2,8,(-2,30),5,1,11,(0,125,0,30,044),078,2,6,5,1,
11,(0,125,0,30,-044),078,2,6,010,5,1,11,(0,119,0,29,044),2,6,5,1,
11,(0,119,0,29,-044),2,6,010,5,1,11,(0,114,0,28,044),2,6,5,1,
11,(0,114,0,28,-044),2,6,010,5,1,11,(0,108,0,27,044),2,6,5,1,
11,(0,108,0,27,-044),2,6,010,5,1,11,(0,102,0,26,044),2,6,5,1,
11,(0,102,0,26,-044),2,6,010,5,1,11,(0,97,0,25,044),2,6,5,1,
11,(0,97,0,25,-044),2,6,010,5,1,11,(0,90,0,24,044),2,6,5,1,
11,(0,90,0,24,-044),2,6,8,(60,-30),0

;; isocp.shp
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
